from maya import cmds


import copy
import operator
import os
import re
import json
from . import read_json_w3
reload(read_json_w3)
from math import degrees
from math import radians
import maya.api.OpenMaya as om

def loadW3File(filename):
    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.json'):
        w3Data = read_json_w3.readW3Data(filename)
    else:
        w3Data = None

    return w3Data

def import_w3_rig(filename):
    print("Importing file: ", filename)
    w3Data = loadW3File(filename)
    if not w3Data:
        return '{NONE}'
    for bone in w3Data.bones:
        cmds.select( d=True )
        if not cmds.objExists(bone.name):
            cmds.joint( name=bone.name, p=(float(bone.co[0]),float(bone.co[1]),float(bone.co[2])), rad=0.1 )
    for bone in w3Data.bones:
            if bone.parentId >= 0:
                try:
                    cmds.parent(bone.name,w3Data.bones[bone.parentId].name)
                except:
                    pass
    for bone in w3Data.bones:
        cmds.select(bone.name);
        cmds.setAttr("{}.translateX".format(bone.name),float(bone.co[0]));
        cmds.setAttr("{}.translateY".format(bone.name),float(bone.co[1]));
        cmds.setAttr("{}.translateZ".format(bone.name),float(bone.co[2]));
    for bone in w3Data.bones:
        cmds.select(bone.name);
        sel_list = om.MSelectionList()
        sel_list.add(bone.name)
        obj = sel_list.getDependNode(0)
        xform = om.MFnTransform(obj)
        xform.setRotation(bone.ro_quat, om.MSpace.kObject)
        # cmds.setAttr("{}.rotateX".format(bone.name),float(-bone.ro[0]));
        # cmds.setAttr("{}.rotateY".format(bone.name),float(-bone.ro[1]));
        # cmds.setAttr("{}.rotateZ".format(bone.name),float(-bone.ro[2]));

def export_w3_rig(filename):
    names = cmds.ls(sl=True,long=False) or []
    parentIdx = []
    positions = []
    rotations = []
    scales = []
    nbBones = len(names)
    output = list()
    for eachSel in names:
        try:
            parent = cmds.listRelatives(eachSel, parent=True)[0]
            parentIdx.append(names.index(parent))
        except:
            parentIdx.append(-1) ##it has no parent
        pos = cmds.xform(eachSel, q= 1, t= 1)
        positions.append({
                        "X": pos[0],
                        "Y": pos[1],
                        "Z": pos[2],
                    })
        rot = cmds.xform(eachSel, q= 1, ro= 1)
        rot_quat = read_json_w3.eularToQuat([-rot[0],-rot[1],-rot[2]])
        rotations.append({
                        "X": rot_quat[0],
                        "Y": rot_quat[1],
                        "Z": rot_quat[2],
                        "W": rot_quat[3]
                    })
        scale = cmds.xform(eachSel, q= 1, s= 1, r=1)
        scales.append({
                        "X": scale[0],
                        "Y": scale[1],
                        "Z": scale[2],
                    })
    output = {"nbBones": nbBones,
                    "names": names,
                    "parentIdx":parentIdx,
                    "positions":positions,
                    "rotations":rotations,
                    "scales":scales}
    with open(filename, "w") as file:
        file.write(json.dumps(output,indent=2, sort_keys=True))

# Define a function
def constrain_w3_rig(filename, ns):
    print("Importing file: ", filename)
    w3Data = loadW3File(filename)
    if not w3Data:
        return '{NONE}'
    for bone in w3Data.bones:
        cmds.select( d=True )
        if cmds.objExists(bone.name) and cmds.objExists("{}:{}".format(ns,bone.name)):
            cmds.parentConstraint( bone.name, "{}:{}".format(ns,bone.name) )
    cmds.confirmDialog( title='Witcher 3',message='The rig has been attached.' )

# Define a function
def export_w3_animation(filename, rig_filename):

    output = list()
    w3Data = loadW3File(rig_filename)
    if not w3Data:
        return '{NONE}'

    bone_frames = {}
    for rig_bone in w3Data.bones:
        bone_frames[rig_bone.name]={
            "positionFrames":[],
            "rotationFrames":[],
            "scaleFrames":[]
        }

    # start time of playback
    start = cmds.playbackOptions(q= 1, min= 1)
    # end time of playback
    end = cmds.playbackOptions(q= 1, max= 1)
    for frame in range(int(start), int(end)+1):
            # move frame
            cmds.currentTime(frame, e= 1)
            # get all locators
            for rig_bone in w3Data.bones:
                try:
                    bone = cmds.select(rig_bone.name);
                    # get position
                    pos = cmds.xform(rig_bone.name, q= 1, t= 1)
                    rot = cmds.xform(rig_bone.name, q= 1, ro= 1)
                    rot_quat = read_json_w3.eularToQuat([-rot[0],-rot[1],-rot[2]])
                    scale = cmds.xform(rig_bone.name, q= 1, s= 1, r=1)
                    if frame is int(start) or cmds.selectKey( rig_bone.name, add=1, time=(frame,frame), k=1, attribute='translateX' ):
                        bone_frames[rig_bone.name]['positionFrames'].append({
                            "x": pos[0],
                            "y": pos[1],
                            "z": pos[2],
                        })
                    if frame is int(start) or cmds.selectKey( rig_bone.name, add=1, time=(frame,frame), k=1, attribute='rotateX' ):
                        bone_frames[rig_bone.name]['rotationFrames'].append({
                            "X": rot_quat[0],
                            "Y": rot_quat[1],
                            "Z": rot_quat[2],
                            "W": rot_quat[3]
                        })
                    if frame is int(start) or cmds.selectKey( rig_bone.name, add=1, time=(frame,frame), k=1, attribute='scaleX' ):
                        bone_frames[rig_bone.name]['scaleFrames'].append({
                            "x": scale[0],
                            "y": scale[1],
                            "z": scale[2],
                        })
                except:
                    bone_frames[rig_bone.name]['positionFrames'].append({
                        "x": 0,
                        "y": 0,
                        "z": 0,
                    })
                    bone_frames[rig_bone.name]['rotationFrames'].append({
                        "X": 0,
                        "Y": 0,
                        "Z": 0,
                        "W": 0
                    })
                    bone_frames[rig_bone.name]['scaleFrames'].append({
                        "x": 0,
                        "y": 0,
                        "z": 0,
                    })
    longestnumframes = 0
    for rig_bone in w3Data.bones:
        #add the first frame
        data = {
            "BoneName": rig_bone.name,
            "position_dt": 0.0333333351,
            "position_numFrames": len(bone_frames[rig_bone.name]['positionFrames']),
            "positionFrames": bone_frames[rig_bone.name]['positionFrames'],
            "rotation_dt": 0.0333333351,
            "rotation_numFrames": len(bone_frames[rig_bone.name]['rotationFrames']),
            "rotationFrames": bone_frames[rig_bone.name]['rotationFrames'],
            "scale_dt": 0.0333333351,
            "scale_numFrames": len(bone_frames[rig_bone.name]['scaleFrames']),
            "scaleFrames": bone_frames[rig_bone.name]['scaleFrames']
        }
        if data['position_numFrames'] >= longestnumframes:
            longestnumframes = data['position_numFrames']
        if data['rotation_numFrames'] >= longestnumframes:
            longestnumframes = data['rotation_numFrames']
        if data['scale_numFrames'] >= longestnumframes:
            longestnumframes = data['scale_numFrames']
        output.append(data)
    output2 = {
        "name": "default_name",
        "bones": output,
        "duration": longestnumframes/float(30),
        "numFrames": longestnumframes,
        "dt": 0.0333333351
    }
    ## WRITING JSON
    # Ensure all folders of the path exist
    with open(filename, "w") as file:
        file.write(json.dumps(output2,indent=2, sort_keys=True))

def loadAnimFile(filename):
    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.json'):
        animData = read_json_w3.readAnimFile(filename)
    else:
        animData = None

    return animData

def import_w3_animation(anim_filename, rig_filename, type="animation"):
    output = list()
    w3Data = loadW3File(rig_filename)
    animData = loadAnimFile(anim_filename)
    if not w3Data:
        return '{NONE}'

    bone_frames = {}
    for rig_bone in w3Data.bones:
        bone_frames[rig_bone.name]={
            "positionFrames":[],
            "rotationFrames":[],
            "scaleFrames":[]
        }
    # start time of playback
    #cmds.playbackOptions(q= 1, min= 1)
    # end time of playback
    #cmds.playbackOptions(q= 1, max= animData.numFrames, aet=animData.numFrames)
    cmds.playbackOptions( min='0', max=str(animData.numFrames), ast='0', aet=str(animData.numFrames))
    # start time of playback
    start = cmds.playbackOptions(q= 1, min= 1)
    # end time of playback
    end = cmds.playbackOptions(q= 1, max= 1)
    for i in range(int(start), int(end)+1):
        # move frame
        cmds.currentTime(i, e= 1)
        for bone in animData.bones:

            ## NEED TO CHECK DT AND SKIP PROPER FRAMES
            if cmds.objExists(bone.BoneName):
                cmds.select(bone.BoneName);
                sel_list = om.MSelectionList()
                sel_list.add(bone.BoneName)
                obj = sel_list.getDependNode(0)
                xform = om.MFnTransform(obj)
                try:
                    bone_frames = len(bone.positionFrames)
                    total_frames = animData.numFrames
                    frame_skip = round(float(total_frames)/float(bone_frames))
                    frame_array = [frame_skip*n for n in range(0,bone_frames)]
                    if float(i) in frame_array:
                        cmds.xform( t=(bone.positionFrames[frame_array.index(i)][0],
                                        bone.positionFrames[frame_array.index(i)][1],
                                        bone.positionFrames[frame_array.index(i)][2]))
                    cmds.setKeyframe( at='translate', itt='spline', ott='spline' )
                except IndexError:
                    pass
                    # handle this
                try:
                    bone_frames = len(bone.rotationFrames)
                    total_frames = animData.numFrames
                    frame_skip = round(float(total_frames)/float(bone_frames))
                    frame_array = [frame_skip*n for n in range(0,bone_frames)]
                    if float(i) in frame_array:
                        xform.setRotation(bone.rotationFrames[frame_array.index(i)], om.MSpace.kObject)
                        #MIMIC POSES DON'T GET INVERTED
                        # if type is "face":
                        #     cmds.xform( ro=(bone.rotationFrames[frame_array.index(i)][0],
                        #                     bone.rotationFrames[frame_array.index(i)][1],
                        #                     bone.rotationFrames[frame_array.index(i)][2]))
                        # else:
                        #     cmds.xform( ro=(-bone.rotationFrames[frame_array.index(i)][0],
                        #                     -bone.rotationFrames[frame_array.index(i)][1],
                        #                     -bone.rotationFrames[frame_array.index(i)][2]))
                    cmds.setKeyframe( at='rotate', itt='auto', ott='auto' )
                except IndexError:
                    pass


def import_w3_face(filename):
    pass
def export_w3_face(filename):
    pass

#witcher3.world()