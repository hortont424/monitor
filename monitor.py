import subprocess
import datetime
import os.path
import platform
import urllib2
from genshi.template import TemplateLoader
from BeautifulSoup import BeautifulSoup

HOSTNAME = "milkyway.cs.rpi.edu"
SERVICE_URL = "http://milkyway.cs.rpi.edu/milkyway/server_status.php"

def ping(hostname):
    if platform.system() == "Darwin" or platform.system() == "BSD":
        cmd = ["ping", "-t", "5", "-o", hostname]
    else:
        cmd = ["ping", "-w", "5", hostname]

    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return proc.wait() == 0

def get_broken_services(url):
    broken = []
    soup = BeautifulSoup(urllib2.urlopen(url).read())

    for row in soup('table')[1]('tr'):
        tds = row('td')

        if len(tds) == 3:
            if tds[2].string != "Running":
                broken.append(tds[0].string)

    return broken

def create_status_page(status):
    status_file = open(os.path.join(os.path.dirname(__file__), "index.html"), "w+")
    loader = TemplateLoader(os.path.join(os.path.dirname(__file__), "templates"), auto_reload=True)

    tmpl = loader.load("index.html")
    status_file.write(tmpl.generate(**status).render("html", doctype="html"))

    status_file.close()

def __main__():
    status = {}

    status["ping"] = ping(HOSTNAME)

    if status["ping"]:
        status["down"] = get_broken_services(SERVICE_URL)

    status["date"] = datetime.datetime.utcnow().strftime("%Y.%m.%d %H:%M:%S")

    create_status_page(status)

if __name__ == "__main__":
    __main__()
