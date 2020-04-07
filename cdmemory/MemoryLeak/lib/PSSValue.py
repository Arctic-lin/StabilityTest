import subprocess, threading, traceback,sys,os
from lib.DrawGraphics import DrawGraphics
import time

class PSSThread(threading.Thread):
    def __init__(self, pid, sample = 2, device = None, caseName="case"):
        super(PSSThread, self).__init__()
        if device:
            self.cmd = ['adb', '-s', device, 'shell', 'dumpsys', 'meminfo', pid]
        else:
            self.cmd = ['adb', 'shell', 'dumpsys', 'meminfo', pid]
        self.pid = pid
        self.caseName = caseName
        self.sample = sample
        self.data=[]
        self.stopFlag = False
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        
    def getPss(self):            
        memoValue = 0
        pro = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True)
#         pro = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = pro.stdout.readline()
#             line = str(pro.stdout.readline())
            line = bytes.decode(line)
            if line == "":
                break
            line = line.strip()
            if line.startswith("TOTAL"):
                memoValue = line.split()[1]
                break
        try:
            if pro.stdout:
                pro.stdout.close()
            if pro.stderr:
                pro.stderr.close()
            if pro.stdin:
                pro.stdin.close()
            pro.kill()
        except Exception:
            traceback.print_exc()
            
        return int(memoValue)
    
    def run(self):
        dirPath = sys.path[0]
        if not os.path.exists(dirPath + "\\report"):
            os.mkdir("report")
        
        if not os.path.exists(dirPath +"\\report\\source_data"):
            os.mkdir(dirPath +"\\report\\source_data")
            
        if not os.path.exists(dirPath +"\\report\\chart"):
            os.mkdir(dirPath +"\\report\\chart")
            
        p=dirPath +"\\report\\source_data\\"+self.caseName+"_"+self.pid+".txt"
#         if os.path.exists(p):
#             os.remove(p)
        f = open(p, 'a')
        while True:
            if self.stopFlag:
                f.close()
                break
            pss = self.getPss()
            currTime = time.time()
            f.write(str(currTime)+', '+str(pss)+"\n")
            self.data.append((int(currTime),pss))
            time.sleep(self.sample-1)

    def stop(self):
        self.stopFlag = True
        self.timeToQuit.set()

class SampleAndReport(object):
    def __init__(self, pids=[], sample=3, device=None, caseName="case"):
        self.pids=pids
        self.sample = sample
        self.device = device
        self.caseName = caseName
        self.threads = []
        self.data = []
        
    def start(self):
        for pid in self.pids:
            p =  PSSThread(pid=pid, sample=self.sample, device=self.device, caseName=self.caseName)
            p.setDaemon(True)
            p.start()
            self.threads.append(p)
    
    def stop(self):
        for t in self.threads:
            self.data.append((t.pid, t.data))
        for t in self.threads:
            t.stop()
        self._report()

    def _report(self):
        for pid, data in self.data:
            d=[]
            d.append(data)
            DrawGraphics(d, pid, "report\\chart\\"+self.caseName+"_"+pid, sampleRate = self.sample) 

if __name__ == "__main__":
    t = PSSThread("com.tct.contacts", device="SWW4UW5XHUCA4L5H")
    t.getPss()

