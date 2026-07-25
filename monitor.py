#!/usr/bin/env python3
"""Generate the ismilkywaydown.com status page from Milkyway@home's server status."""

import datetime
import os.path
import urllib.error
import urllib.request

from bs4 import BeautifulSoup
from genshi.template import TemplateLoader

SERVICE_URL = "https://milkyway.cs.rpi.edu/milkyway/server_status.php"

# A large assimilation backlog means work is being validated but not written
# out, which is a stall even when every daemon reports "Running".
ASSIMILATOR_BACKLOG_LIMIT = 10000

HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ismilkywaydown.com"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def cell_text(cell):
    return cell.get_text(strip=True)


def daemon_rows(soup):
    """Rows of the daemon status table, as (name, host, status).

    Found by shape rather than by position: the first table containing rows of
    exactly three cells. The page's table order has changed before, and looking
    it up by index is what silently broke this script.
    """
    for table in soup("table"):
        rows = [row for row in table("tr") if len(row("td")) == 3]
        if rows:
            return rows
    return []


def labelled_value(soup, label):
    """Look up a two-column statistic by its label, wherever it lives."""
    for table in soup("table"):
        for row in table("tr"):
            cells = row("td")
            if len(cells) == 2 and cell_text(cells[0]) == label:
                return cell_text(cells[1])
    return None


def broken_services(html):
    soup = BeautifulSoup(html, "html.parser")
    broken = set()

    for row in daemon_rows(soup):
        name, _host, status = (cell_text(cell) for cell in row("td"))
        if status != "Running":
            broken.add(name)

    backlog = labelled_value(soup, "Workunits waiting for assimilation")
    if backlog is not None:
        try:
            if int(backlog.replace(",", "")) > ASSIMILATOR_BACKLOG_LIMIT:
                broken.add("assimilator backlog")
        except ValueError:
            pass

    return broken


def write_status_page(status):
    loader = TemplateLoader(os.path.join(HERE, "templates"), auto_reload=False)
    template = loader.load("index.html")
    page = template.generate(**status).render("html", doctype="html")

    with open(os.path.join(HERE, "index.html"), "w") as status_file:
        status_file.write(page)


def main():
    # `reachable` is whether the status page itself answered. That is the
    # question the site is really asking — a host that replies to ICMP while
    # its services are unreachable is down for every purpose that matters here.
    status = {"reachable": True, "down": []}

    try:
        html = fetch(SERVICE_URL)
    except (urllib.error.URLError, OSError):
        status["reachable"] = False
    else:
        # sorted() so the rendered page is stable when the set of broken
        # services has not actually changed.
        status["down"] = sorted(broken_services(html))

    # The page shows this in the reader's own timezone, so it goes out as a
    # machine-readable instant. `date` is only the no-JS fallback, and it says
    # UTC out loud — an unlabelled UTC time reads as a wrong local time.
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    status["date"] = now.strftime("%Y.%m.%d %H:%M:%S UTC")
    status["date_iso"] = now.isoformat()

    write_status_page(status)


if __name__ == "__main__":
    main()
