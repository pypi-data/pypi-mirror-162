import os
from ..Process.Multiprocess.SubProcessWorker import SubProcessWorkerClass
from ..File import Path

class MayaSubProcessWorker(SubProcessWorkerClass):
    def __init__(self, cpuID, MayaVersion, Command, LogFilter, CommandFilter):
        MayaPath = Path.GetMayaPath(MayaVersion)
        if MayaPath:
            MayaPyPath = os.path.join(MayaPath, '/bin/mayapy.exe')
        super(MayaSubProcessWorker, self).__init__(cpuID, MayaPyPath, Command, LogFilter, CommandFilter)