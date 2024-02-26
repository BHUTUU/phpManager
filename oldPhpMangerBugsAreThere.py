# Program: Manage php server that includes serving, and killing the running servers.
# Author: Suman Kumar ~BHUTUU
# Date: 7 January 2024
# Compatible with Windows and Linux(Debian based) only included Termux.
import os, subprocess, sys, threading, re, time
class PhpManager:
    winPhp = "C:\\Program Files\\php"
    if os.name == "nt":
        sys.path.append(winPhp)
    __pids=[] 
    __serversAndPid={}
    @classmethod
    def __runServer__(cls, lhost, lport):
        os.system(f"php -S {lhost}:{lport} 2> {os.devnull}")
        return True
    @classmethod
    def __getNewPhpPid(cls):
        validPid = None
        if os.name == "nt":
            try:
                rawPids = subprocess.check_output("tasklist | findstr php", shell=True)
                rawPids = rawPids.decode('utf-8')
            except subprocess.CalledProcessError:
                return validPid
            if rawPids:
                allPids = re.findall(r'php\.exe\s+(\d+)', rawPids)
            else:
                return validPid
        elif os.name == 'posix':
            try:
                rawPids = subprocess.check_output("pgrep -af php | awk '{print $1}'")
                rawPids = rawPids.decode('utf-8')
                try:
                    rawPids.remove(' ')
                except:
                    pass
                try:
                    rawPids.remove(None)
                    allPids=rawPids
                except:
                    pass
            except:
                return validPid
        else:
            return validPid
        newPid = []
        for pid in allPids:
            if pid not in PhpManager.__pids:
                newPid.append(pid)
            # else:
            #     pass
        return newPid
    @classmethod
    def __pidOfServer__(cls): # this must be ran just after starting the new server to get the pid of that particular server.
        validPid = None
        newPids = PhpManager.__getNewPhpPid()
        if newPids:
            if len(newPids) == 1:
                PhpManager.__pids.extend(newPids)
                validPid = newPids[0]
                return validPid
    @staticmethod
    def startServer(lhost: str, port: int):
        __key=f"{lhost}:{port}"
        if PhpManager.__serversAndPid.get(__key) is not None:
            __pidOfThisAlreadyRunnigServer = PhpManager.__serversAndPid.get(__key)
            return [False, f"This server is already in use and pid is {__pidOfThisAlreadyRunnigServer}"]
        threading.Thread(target=PhpManager.__runServer__, args=[lhost, port]).start()
        time.sleep(0.2)
        thisPid = PhpManager.__pidOfServer__()
        PhpManager.__serversAndPid[__key]=thisPid
        # print("server started")
        return [True, thisPid]
    @staticmethod
    def killServer(lhost: str, port: int):
        __key=f"{lhost}:{port}"
        if __key in PhpManager.__serversAndPid.keys():
            __pidToKill = int(PhpManager.__serversAndPid.get(__key))
            try:
                os.kill(__pidToKill, 9)
            except OSError as e:
                return [False, e]
            del PhpManager.__serversAndPid[__key]
            return [True, "Server killed Successfully"]
        return [False, "Invalid PHP Server instance to Kill"]
    @staticmethod
    def getPidOf(lhost: str, port: int):
        __key=f'{lhost}:{port}'
        if PhpManager.__serversAndPid.get(__key) is not None:
            return int(PhpManager.__serversAndPid.get(__key))
        return None
    @staticmethod
    def getAllPids(outputType="list"):
        if outputType == "list":
            return list(PhpManager.__serversAndPid.values())
        if outputType == "dict":
            return dict(PhpManager.__serversAndPid)
        else:
            return None
    @staticmethod
    def getAllRunningServers():
        __serverlist = []
        try:
            for i in PhpManager.__serversAndPid.keys():
                __serverlist.append(tuple(i.split(":")))
            return __serverlist
        except:
            return None