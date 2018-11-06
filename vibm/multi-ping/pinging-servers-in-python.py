import os

import subprocess 

from dynaconf import settings 

print(settings.HOST)

# example No1
hostname = "google.com"

# example No2
# hostname = 'icache'

response = os.system("ping -c 1 " + hostname)

ping_response = subprocess.Popen(["/bin/ping", "-c", "1", "192.169.0.1"], stdout=subprocess.PIPE).stdout.read()
print("Recipy 2: ", ping_response)

if subprocess.check_output(["ping", "-c", "1", hostname]):
    print("My Found It")
else:
    print("My Lost It") 

# check the response ...
if response == 0:
    print( hostname, 'is Up!')
else:
    print( hostname, 'is Down!')