import socket
import errno
from concurrent.futures import ThreadPoolExecutor,as_completed
import threading,time

class RateLimiter:
    def __init__(self,per_second):
        self.interval=1.0/per_second
        self.lock=threading.Lock()
        self.next_time=time.monotonic()

    def wait(self):
        with self.lock:
            now=time.monotonic()
            if now<self.next_time:
                time.sleep(self.next_time-now)
            self.next_time=max(now,self.next_time)+self.interval

limiter=RateLimiter(50)

def scan_port(host,port,timeout,limiter):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(timeout)

    limiter.wait()

    banner=""

    try:
        result=s.connect_ex((host,port))
    except socket.timeout:
        s.close()
        return port,"filtered",banner

    if(result==0):
        try:
            banner=s.recv(1024).decode(errors='ignore').strip()
        except socket.timeout:
            banner=""
        s.close()
        return port,"open",banner
    elif(result==errno.ECONNREFUSED):
        s.close()
        return port,"closed",banner
    else:
        s.close()
        return port,"filtered",banner

host="scanme.nmap.org"
timeout=1

results=[]
banners=[]

with ThreadPoolExecutor(max_workers=200) as executor:
    futures={executor.submit(scan_port,host,port,timeout,limiter):port for port in range(1,1001)}

    for future in as_completed(futures):
        port,state,banner=future.result()
        results.append((port,state))
        if state=="open":
            if banner=="":
                try:
                    banner=socket.getservbyport(port)
                except OSError:
                    banner="Unknown"
            banners.append((port,banner))

print(results)
print(banners)
