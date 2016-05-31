# -*- coding:utf-8 -*-
import os
import sys,getopt
import urllib2
from BeautifulSoup import BeautifulSoup
from multiprocessing import Process,Queue,Lock

reload(sys)
sys.setdefaultencoding('utf-8')

def usage():
    print "This is a Program to get proxyIP.\n\
         Usage:\n\
             -o    Output file.\n\
             -d    Process number, default is 1.\n\
             -n    Page number, default is 1.\n\
             -v    Version.\n\
             -h    Help.\n\n\
     Write by Aunity\n\
     Version 1.0.1\n\
     Update time: 2016-5-24"
    sys.exit(0)

def main():
    rsPath = ""
    proN = 11
    pageN = 1
    try:
        opts,args = getopt.getopt(sys.argv[1:],"d:n:vho:",['help=','version=']);print opts,args
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    for opt,arg in opts:
        if opt in ("-v","--version"):
            print "Version 1.0.1";sys.exit(0)
        elif opt in ("-h","--help"):
            usage();break
        elif opt =="-o":
            rsPath = arg;continue
        elif opt=="-n":
            pageN = int(arg);continue
        elif opt=="-d":
            proN = int(arg)
        else:
            assert False, "unhandled option"
    return rsPath,proN,pageN

class Proxy(object):
    def __init__(self):
        object.__init__(self)
        
    def setConnect(self,url):
        request = urllib2.Request(url)
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
        request.add_header('User-Agent',user_agent)
        return request
    
    def splitHTML(self,Q,html):
        soup = BeautifulSoup(html)
        IPtable = soup.find('table',attrs={"id" : "ip_list"})
        IPtrs = IPtable.findAll('tr')
        for IPtr in IPtrs[1:-1]:
            tds = IPtr.findAll("td")
            IP = ":".join(( td.text for td in tds[1:3] ))
            Q.put(IP)
        return Q
           
    def proxyTest(self,lock,ipsQ,IPs):
        PID = os.getpid()
        while not ipsQ.empty():
            lock.acquire()
            ip = ipsQ.get()
            lock.release()
            if not ip:
                return
            url = 'http://ip.chinaz.com/getip.aspx'
            urllib2.socket.setdefaulttimeout(20)
            request = self.setConnect(url)
            request.set_proxy(ip,'http')
            response = -1
            print "PID: %s  IP: %s" %(PID,ip)
            try:
                response = urllib2.urlopen(request)
            except:
                continue
            else:
                if response.code==200:
                    lock.acquire()
                    IPs.put(ip)
                    lock.release()

    def getIP(self,lock,ipsQ):
        while not ipsQ.empty():
            lock.acquire()
            ip = ipsQ.get()
            lock.release()

    def save(self,rsPath,IPs):
        fw = open(rsPath,'w')
        while not IPs.empty():
            ip = IPs.get()
            fw.write(ip+"\n")
        fw.close()


if __name__=="__main__":
    rsPath,proN,pageN = main()
    proxy = Proxy()
    url = 'http://www.xicidaili.com/nn/'

    lock = Lock()
    ipsQ = Queue();IPs = Queue()
    for i in xrange(1,pageN+1):
        temp = url + str(i);print temp
        request = proxy.setConnect(temp)
        response = urllib2.urlopen(request)
        ipsQ = proxy.splitHTML(ipsQ,response.read())

    P = []
    for num in xrange(proN):
        P.append(Process(target = proxy.proxyTest, args = (lock,ipsQ,IPs,)));P[-1].start();
    for p in P:
        p.join()
    proxy.save(rsPath,IPs)

