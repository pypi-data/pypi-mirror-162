import os
import json
from ..File import Path

def ReadJson(JsonPath):
    if os.path.exists(JsonPath):
        with open(JsonPath, 'r') as json_file:
            Result = json.load(json_file)
        return Result
    else:
        print('Json file is not exists')
        return None

def MakeJson(TargetPath, FileName, ExportData):
    Path.MakeDirectory(TargetPath)
    if os.path.exists(TargetPath):
        FinalFileName = os.path.join(TargetPath, FileName)
        if '.json' not in FileName:
            FinalFileName = FinalFileName + '.json'
        try:
            with open(FinalFileName, 'w') as json_file:
                json.dump(ExportData, json_file, indent=2)
        except:
            print('Json export failed')