import os
import subprocess

pid = 1234
process = subprocess.Popen('netstat -ano | find "{}"'.format(pid), shell=True, stdout=subprocess.PIPE)

output = str(process.communicate()[0])
port = output[output.find(":") + 1:output.find(" ", output.find(":"))]
print(output)
print(port)

if output:
    print("ok")
