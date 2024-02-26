import os, sys, subprocess, threading, re, time

class PhpManager:
    #<<<--------Declaring class variables---------->>>
    __pids=[] 
    __serversAndPid={}
    __phpLogFiles=[]
    if os.name == "nt":
        winPhp = "C:\\Program Files\\php"
        sys.path.append(winPhp)
    #<<<-------Checking and installing php if not found----------->>>
    if os.name == "posix":
        #<<<----for termux------>>>
        if "/data/data/com.termux/files" in os.getcwd():
            if not os.path.isfile("/data/data/com.termux/files/usr/bin/php"):
                try:
                    os.system("apt instal php -y")
                except OSError:
                    sys.stderr.write("coundt find php binary. Please install it manually\n")
                    exit(1)
        #<<<----for other debian------>>>
        else:
            if not os.path.isfile("/usr/bin/php"):
                try:
                    os.system("sudo apt instal php -y")
                except OSError:
                        sys.stderr.write("coundt find php binary. Please install it manually\n")
                        exit(1)
    #<<<-----for windows------>>>
    elif os.name == 'nt':
        if not os.path.isfile(os.path.join(winPhp, "php.exe")):
            try:
                import setup # here i want a new setup method later.
            except:
                sys.stderr.write("coundt find php binary. Please install it manually\nyou have to install php and add in the path environment variable manually\n")
                exit(1)

    #<<<<----declaring classmethods--------->>>
    @classmethod
    def __runServer__(cls, lhost, lport, logFile):
        os.system(f"php -S {lhost}:{lport} 2> {logFile}")
        return True
    @classmethod
    def __getNewPhpPid(cls):
        validPid = None
        allPids=[]
        if os.name == "nt":
            try:
                rawPids = subprocess.check_output("tasklist | findstr php", shell=True)
                rawPids = rawPids.decode('utf-8')
            except subprocess.CalledProcessError:
                return validPid
            if rawPids:
                allPids = re.findall(r'php\.exe\s+(\d+)', rawPids)
                if '' in allPids:
                    allPids.remove('')
                if None in allPids:
                    allPids.remove(None)
            else:
                return validPid
        elif os.name == 'posix':
            try:
                rawPids = subprocess.check_output("pgrep -af php | awk '{print $1}'", shell=True)
                rawPids = rawPids.decode('utf-8')
            except subprocess.CalledProcessError:
                return validPid
            if rawPids:
                allPids = list(rawPids.split("\n"))
                if '' in allPids:
                    allPids.remove('')
                if None in allPids:
                    allPids.remove(None)
            else:
                return validPid
        else:
            return "Invalid os please contact me on https://bhutuu.github.io"
        newPid = []
        for pid in allPids:
            if pid not in PhpManager.__pids:
                newPid.append(pid)
                print(pid)
        return newPid
    @classmethod
    def __pidOfServer__(cls):
        validPid = None
        newPids = PhpManager.__getNewPhpPid()
        validPid = newPids[-1]
        return validPid  
    #<<<-----declaring staticmethods -------->>>
    @staticmethod
    def startServer(lhost: str, lport: int, logOutputPath: str = os.path.join(os.getcwd(),"PhpServerLog.txt")):
        if logOutputPath in PhpManager.__phpLogFiles:
            sys.stdout.write("this log file is already in use by another php session. Try again using different file name\n")
            return [False, f"this log file is already in use by another php session. Try again using different file name"]
        _key=f"{lhost}:{lport}"
        if PhpManager.__serversAndPid.get(_key) is None:
            threading.Thread(target=PhpManager.__runServer__, args=[lhost, lport, logOutputPath]).start()
            time.sleep(0.2)
            thisPid = PhpManager.__pidOfServer__()
            PhpManager.__serversAndPid[_key]=thisPid
            # print("server started")
            return [True, thisPid, '{"log_path": '+ f'\"{logOutputPath}\"'+"}"]
    @staticmethod
    def killServer(lhost: str, lport: int):
        _key = f"{lhost}:{lport}"
        if _key in PhpManager.__serversAndPid.keys():
            __pidToKill = int(PhpManager.__serversAndPid.get(_key))
            try:
                os.kill(__pidToKill, 9)
            except OSError:
                sys.stderr.write(f"unable to kill pid: {__pidToKill}. kill it manually.\n")
                return [False, f"unable to kill pid: {__pidToKill}. kill it manually.\n"]
            del PhpManager.__serversAndPid[_key]
            return [True, "Server killed Successfully"]
        return [False, "Invalid PHP server instance to kill"]
    @staticmethod
    def getPidOf(lhost: str, port: int):
        __key=f'{lhost}:{port}'
        if PhpManager.__serversAndPid.get(__key) is not None:
            return [True, PhpManager.__serversAndPid.get(__key)]
        return None
    @staticmethod
    def getAllPids(outputType: str ="list"):
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
                if PhpManager.__serversAndPid.get(i) is not None:
                    __serverlist.append(PhpManager.__serversAndPid.get(i))
            return __serverlist
        except:
            return None