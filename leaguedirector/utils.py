import os
import psutil
import subprocess


def find_procs_by_name(name):
    "Return a list of processes matching 'name'."
    assert name, name
    ls = []
    for p in psutil.process_iter():
        name_, exe, cmdline = "", "", []
        try:
            name_ = p.name()
            cmdline = p.cmdline()
            exe = p.exe()
        except (psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except psutil.NoSuchProcess:
            continue
        if name == name_ or (len(cmdline) > 0 and cmdline[0] == name) or os.path.basename(exe) == name:
            ls.append(p)
    return ls


def find_port_by_pid(pid):
    process = subprocess.Popen('netstat -ano | find "{}"'.format(pid), shell=True, stdout=subprocess.PIPE)
    output = str(process.communicate()[0])
    port = output[output.find(":") + 1:output.find(" ", output.find(":"))]

    return int(port)
