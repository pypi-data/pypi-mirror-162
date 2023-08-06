import subprocess
from queue import Queue, Empty
from threading import Thread

from ...Data.Enums import WorkStatus
from ...Data.Static import DefaultCommandFilter, DefaultLogFilter

WaitingCode = '''
import sys
for line in sys.stdin:
    pass
'''

class SubProcessWorkerClass(object):
    def __init__(self, cpuID, ExcutePath, Command, LogFilter=DefaultLogFilter, CommandFilter=DefaultCommandFilter):
        self.cpuID = cpuID
        self.ExcutePath = ExcutePath
        self.Command = Command
        self.LogFilter = LogFilter
        self.CommandFilter = CommandFilter
        self.Log = []
        self.Status = WorkStatus.Wait
        
    def Run(self):
        self.Status = WorkStatus.Run
        self.SubProcess = subprocess.Popen(f'{self.ExcutePath} {self.Command}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, text=True, shell=False)
        self.SubProcessOutputQueue = Queue()
        self.ReadThread = Thread(target=self.LiveOutput, args=(self.SubProcess.stdout, self.SubProcessOutputQueue))
        self.ReadThread.daemon = True
        self.ReadThread.start()

    def LiveOutput(self, out, queue):
        for line in iter(out.readline, b''):
            if self.LogFilter in line:
                self.Log.append(line)
            queue.put(line)
        out.close
    
    def GetLog(self):
        return self.Log

    def GetStdOut(self):
        Result=[]
        try:
            while True:
                Result.append(self.SubProcessOutputQueue.get_nowait())
        except Empty:
            return Result

    def SendMsg(self, Msg):
        self.SubProcess.stdin.write(f'{self.CommandFilter} {Msg}')
        self.SubProcess.stdin.flush()


# class SubProcessWorker_Maya(SubProcessWorkerClass):
#     def __init__(self, Command, Version):
#         MayaPath, _ = PathManager.GetMayaPath(str(Version))
#         MayabatchPath = os.path.join(MayaPath, 'bin\\mayabatch.exe')
#         super().__init__(self, MayabatchPath, Command)
        

# class SubProcessWorker_Unreal(SubProcessWorkerClass):
#     def __init__(self, Command, Version):
#         UnrealPath, _ = PathManager.GetEnginePath(str(Version))
#         UnrealCommandLetPath = os.path.join(UnrealPath, '\\Engine\\Binaries\\Win64\\UE4Editor-Cmd.exe')
#         super().__init__(self, UnrealCommandLetPath, Command)