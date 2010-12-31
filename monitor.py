import subprocess
import json
import copy
import datetime

def ping(hostname):
    cmd = ["ping", "-t", "5", "-o", hostname]
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return proc.wait() == 0

def load_config(filename):
    config = json.load(open(filename, "r"))
    return config

def __main__():
    config = load_config("config.json")

    for (name, project) in config["projects"].items():
        for (index, (hostname, title)) in enumerate(project["ping_hosts"]):
            project["ping_hosts"][index].append(ping(hostname))

    config["date"] = datetime.datetime.utcnow().isoformat()

    print json.dumps(config, sort_keys=True, indent=4)

if __name__ == "__main__":
    __main__()
