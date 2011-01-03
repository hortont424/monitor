import subprocess
import json
import copy
import datetime
import os.path
import platform

HOSTNAME = "milkyway.cs.rpi.edu"

def ping(hostname):
    if platform.system() == "Darwin" or platform.system() == "BSD":
        cmd = ["ping", "-t", "5", "-o", hostname]
    else:
        cmd = ["ping", "-w", "5", hostname]

    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return proc.wait() == 0

def write_config(filename, config):
    file = open(filename, "w+")
    file.write(json.dumps(config, sort_keys=True, indent=4))
    file.close()

def __main__():
    dir = os.path.dirname(__file__)
    config = {}

    config["ping"] = ping(HOSTNAME)
    config["date"] = datetime.datetime.utcnow().strftime("%Y.%m.%d %H:%M:%S")

    write_config(os.path.join(dir, "output.json"), config)

if __name__ == "__main__":
    __main__()
