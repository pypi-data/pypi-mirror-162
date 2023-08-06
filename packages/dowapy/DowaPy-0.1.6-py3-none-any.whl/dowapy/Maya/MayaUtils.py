import os

from dowapy.File import Path, Json
from dowapy.Data import NamingRule

from maya import cmds
from maya import mel
from pymel import core

def ImportReference():
    ReferenceNodeList = cmds.ls(type='reference')
    for ReferenceNode in ReferenceNodeList:
        print('Reference : %s' %ReferenceNode)
        if ReferenceNode == 'sharedReferenceNode':
            continue
        if cmds.referenceQuery(ReferenceNode, isLoaded=True):
            ReferenceFile = cmds.referenceQuery(ReferenceNode, f=True)
            cmds.file(ReferenceFile, importReference=True)

def CheckReference(LowKeywords, ReplaceKeyword):
    ReferenceNodeList = cmds.ls(type='reference')
    for ReferenceNode in ReferenceNodeList:
        if ReferenceNode == 'sharedReferenceNode':
            continue
        CapitalizedPath = ReferenceNode.upper()
        for LowKeyword in LowKeywords:
            if LowKeyword in CapitalizedPath:
                ReplaceReference(ReferenceNode, LowKeyword, ReplaceKeyword)
                continue

def ReplaceReference(Target, OriginKeyword, NewKeyword):
    ReferencePath = cmds.referenceQuery(Target, filename=True).partition('{')[0]
    NewReferencePath = ReferencePath.replace(OriginKeyword, NewKeyword)
    if os.path.exists(NewReferencePath) and NewReferencePath != ReferencePath:
        cmds.file(NewReferencePath, loadReference=Target, type='mayaAscii', options='v=1;')

def GimbalSolver(JointObject):
    cmds.select(JointObject)
    ChildrenJoints = cmds.listRelatives(allDescendents=True, type='joint')
    cmds.select(ChildrenJoints, add=True)

    Objects = cmds.ls(sl=True)
    ObjectFirstFrame = cmds.playbackOptions(q=True, min=True)
    ObjectEndFrame = cmds.playbackOptions(q=True, max=True)

    cmds.bakeSimulation(Objects, t=(ObjectFirstFrame, ObjectEndFrame))

    for Object in Objects:
        CurrentAnimCurve = cmds.listConnections(Object, d=False, type='animCurve')
        cmds.filterCurve(CurrentAnimCurve, filter='euler')

def OpenMayaScene(FilePath):
    try:
        cmds.file(FilePath, o=True, force=True, executeScriptNodes=True)
        print('Open Success')
        return 0
    except:
        print('*** Maya Fatal Error ***')
        return 1

def FBXExport(Pair, OutputPath, PresetPath, FirstFrame, EndFrame, GimberSolver = False):
    cmds.select(Pair['Joint'], r=True)
    if GimberSolver:
        GimbalSolver(cmds.ls(sl=1))
    cmds.select(Pair['Model'], add=True)
    if not os.path.exists(OutputPath):
        print("Export Start with [ %s ]" % cmds.ls(sl=True, sn=True))
        mel.eval('FBXLoadExportPresetFile -f ("%s")' % PresetPath)
        mel.eval("FBXExportBakeComplexStart -v %d" % FirstFrame)
        mel.eval("FBXExportBakeComplexEnd -v %d" % EndFrame)
        mel.eval("FBXExportShapes -v true")
        mel.eval('FBXExport -f ("%s") -s' % OutputPath)
        print("Export Done : [%s]" % OutputPath)
    else:
        print("Already exported object : [%s]" % OutputPath)
