import subprocess
import json
import copy
import datetime
import os.path
import platform

def ping(hostname):
    if platform.system() == "Darwin" or platform.system() == "BSD":
        cmd = ["ping", "-t", "5", "-o", hostname]
    else:
        cmd = ["ping", "-w", "5", hostname]

    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return proc.wait() == 0

def load_config(filename):
    file = open(filename, "r")

    if not file:
        print "Failed to open configuration file '{0}'...".format(filename)

    config = json.load(file)
    file.close()

    return config

def write_config(filename, config):
    file = open(filename, "w+")
    file.write(json.dumps(config, sort_keys=True, indent=4))
    file.close()

def __main__():
    dir = os.path.dirname(__file__)
    config = load_config(os.path.join(dir, "config.json"))

    for (name, project) in config["projects"].items():
        for (index, (hostname, title)) in enumerate(project["ping_hosts"]):
            project["ping_hosts"][index].append(ping(hostname))

    config["date"] = datetime.datetime.utcnow().isoformat()

    write_config(os.path.join(dir, "output.json"), config)

if __name__ == "__main__":
    __main__()
