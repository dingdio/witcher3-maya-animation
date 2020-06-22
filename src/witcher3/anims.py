from maya import cmds
import copy
import operator
import os
import re
import json
import import_rig
import read_json_w3
reload(read_json_w3)
import fbx_util
reload(fbx_util)
from math import degrees
from math import radians
import maya.api.OpenMaya as om
import maya.OpenMaya as OpenMaya
import pymel.core as pm
import maya.mel as mel

# from enum import Enum
# anim_type = Enum('anim_type', ['animation', 'face'])

def export_w3_animation(filename, rig_filename, anim_name ="default_name", scene_actor=""):

    output = list()
    w3Data = import_rig.loadW3File(rig_filename)
    if not w3Data:
        return '{NONE}'

    bones = w3Data.bones
    # start time of playback
    start = int(cmds.playbackOptions(q= 1, min= 1))
    # end time of playback
    end = int(cmds.playbackOptions(q= 1, max= 1)+1)
    final_output = export_w3_animation2(
        filename,
        start,
        end,
        bones,
        anim_name,
        scene_actor
    )
    ## WRITING JSON
    # Ensure all folders of the path exist
    with open(filename, "w") as file:
        file.write(json.dumps(final_output,indent=2, sort_keys=True))



def export_w3_animation2(filename, start, end, bones, anim_name ="default_name", scene_actor=""):
    bone_frames = {}
    for rig_bone in bones:
        bone_frames[rig_bone.name]={
            "positionFrames":[],
            "rotationFrames":[],
            "scaleFrames":[]
        }
    output = list()
    for frame in range(start, end):
            # move frame
            cmds.currentTime(frame, e= 1)
            # get all locators
            for bone in bones:
                boneName = bone.name+""
                base_boneName = bone.name
                if scene_actor:
                    boneName = scene_actor+":"+bone.name
                try:
                    bone = cmds.select(boneName);
                    # get position
                    pos = cmds.xform(boneName, q= 1, t= 1)
                    rot = cmds.xform(boneName, q= 1, ro= 1)
                    rot_quat = read_json_w3.eularToQuat([-rot[0],-rot[1],-rot[2]])
                    scale = cmds.xform(boneName, q= 1, s= 1, r=1)
                    if frame is int(start) or cmds.selectKey( boneName, add=1, time=(frame,frame), k=1, attribute='translateX' ):
                        bone_frames[base_boneName]['positionFrames'].append({
                            "x": pos[0], #format(pos[0], '.5f')
                            "y": pos[1],
                            "z": pos[2],
                        })
                    if frame is int(start) or cmds.selectKey( boneName, add=1, time=(frame,frame), k=1, attribute='rotateX' ):
                        bone_frames[base_boneName]['rotationFrames'].append({
                            "X": rot_quat[0],
                            "Y": rot_quat[1],
                            "Z": rot_quat[2],
                            "W": rot_quat[3]
                        })
                    if frame is int(start) or cmds.selectKey( boneName, add=1, time=(frame,frame), k=1, attribute='scaleX' ):
                        bone_frames[base_boneName]['scaleFrames'].append({
                            "x": scale[0],
                            "y": scale[1],
                            "z": scale[2],
                        })
                except:
                    bone_frames[base_boneName]['positionFrames'].append({
                        "x": 0,
                        "y": 0,
                        "z": 0,
                    })
                    bone_frames[base_boneName]['rotationFrames'].append({
                        "X": 0,
                        "Y": 0,
                        "Z": 0,
                        "W": 0
                    })
                    bone_frames[base_boneName]['scaleFrames'].append({
                        "x": 0,
                        "y": 0,
                        "z": 0,
                    })
    longestnumframes = 0

    #Bone name should not have any namespace at this point.
    for bone in bones:
        boneName = bone.name
        #add the first frame
        data = {
            "BoneName": boneName,
            "position_dt": 0.0333333351,
            "position_numFrames": len(bone_frames[boneName]['positionFrames']),
            "positionFrames": bone_frames[boneName]['positionFrames'],
            "rotation_dt": 0.0333333351,
            "rotation_numFrames": len(bone_frames[boneName]['rotationFrames']),
            "rotationFrames": bone_frames[boneName]['rotationFrames'],
            "scale_dt": 0.0333333351,
            "scale_numFrames": len(bone_frames[boneName]['scaleFrames']),
            "scaleFrames": bone_frames[boneName]['scaleFrames']
        }
        if data['position_numFrames'] >= longestnumframes:
            longestnumframes = data['position_numFrames']
        if data['rotation_numFrames'] >= longestnumframes:
            longestnumframes = data['rotation_numFrames']
        if data['scale_numFrames'] >= longestnumframes:
            longestnumframes = data['scale_numFrames']
        output.append(data)
    duration = longestnumframes * 0.0333333351;
    animBuffer = {
        "version": 0,
        "bones": output,
        "tracks": None,
        "duration": duration,
        "numFrames": longestnumframes,
        "dt": 0.0333333351
    }

    animation={
        "name": anim_name,
        "motionExtraction": {
        "duration": 2.0,
        "frames": [
            0.0,
            0.0543115139,
            0.267023444,
            1.64584517,
            1.86751282,
            1.98472381,
            1.99999952
        ],
        "deltaTimes": [],
        "flags": 2
        },
        "animBuffer": animBuffer,
        "framesPerSecond": 30.0,
        "duration": duration
    }
    animationSetEntry={
        "animation": animation,
        "entries":[]
    }
    return animationSetEntry


def loadAnimFile(filename):
    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.json'):
        with open(filename) as file:
            data = file.read()
            animJson = json.loads(data)
            animData = read_json_w3.readSkeletalAnimationSetEntry(animJson)
    else:
        animData = None

    return animData

def import_w3_animation(anim_filename, scene_actor, type="animation"):
    SkeletalAnimationSetEntry = loadAnimFile(anim_filename)
    if not SkeletalAnimationSetEntry:
        return '{NONE}'
    return import_w3_animation2(SkeletalAnimationSetEntry.animation, scene_actor, type)

#Witcher animations start at frame 0
def import_w3_animation2(SkeletalAnimation, scene_actor, type, al=False):
    SkeletalAnimationData = SkeletalAnimation.animBuffer
    multipart = False
    if hasattr(SkeletalAnimationData, 'parts'):
        multipart=True
    if type is not "face":
        cmds.playbackOptions( min='0', max=str(SkeletalAnimationData.numFrames-1), ast='0', aet=str(SkeletalAnimationData.numFrames-1))
    if multipart:
        for part_index in range(0, len(SkeletalAnimationData.parts)):
        #for part_index in range(10, 11):
            print(part_index)
            animData = SkeletalAnimationData.parts[part_index]
            firstFrame = int(SkeletalAnimationData.firstFrames[part_index])
            start = 0
            end = animData.numFrames
            addAnimation(animData, scene_actor, start, end, firstFrame, type, al)
    else:
        animData = SkeletalAnimationData
        firstFrame = 0
        start = 0
        end = animData.numFrames
        addAnimation(animData, scene_actor, start, end, firstFrame, type, al)
    return SkeletalAnimation

def addAnimation(animData, scene_actor, start, end, firstFrame, type, al):
    global_weight = 1.0 #0.66

    #
    face_animation = False
    if(animData.tracks):
        face_animation = True

    
    #CODE TO CREATE AND NEW LAYER FOR THIS ANIMATION
    # pm.animation.animLayer(scene_actor+"_addLayer", weight=1.0)
    # al = scene_actor+"_addLayer"

    for fi in range(int(start), int(end)):
        time_index=firstFrame+fi
        #if not animData.tracks:

        for bone in animData.bones:
            ## NEED TO CHECK DT AND SKIP PROPER FRAMES
            boneName = bone.BoneName+""
            if scene_actor:
                boneName = scene_actor+":"+bone.BoneName

            #CODE TO CREATE AND NEW LAYER FOR THIS ANIMATION
            # pm.select(boneName)
            # pm.animation.animLayer(scene_actor+"_addLayer", edit=True, addSelectedObjects=True)

            if cmds.objExists(boneName):
                cmds.select(boneName);
                sel_list = om.MSelectionList()
                sel_list.add(boneName)
                obj = sel_list.getDependNode(0)
                xform = om.MFnTransform(obj)
                orig_rotation = xform.rotation(om.MSpace.kObject, asQuaternion=True)
                try:
                    bone_frames = len(bone.positionFrames)
                    if bone_frames is 1 and bone.positionFrames[0].count(0.0) == 3: #for face animations that pass in 0s that are not used, might cause issues?
                        pass
                    else:
                        total_frames = animData.numFrames
                        frame_skip = round(float(total_frames)/float(bone_frames))
                        frame_array = [frame_skip*n for n in range(0,bone_frames)]
                        if float(fi) in frame_array:
                            cmds.xform( t=(bone.positionFrames[frame_array.index(fi)][0],
                                            bone.positionFrames[frame_array.index(fi)][1],
                                            bone.positionFrames[frame_array.index(fi)][2]))
                            if al:
                                pm.setKeyframe(boneName, t=time_index, at='translate', al=al)
                            else:
                                pm.setKeyframe(boneName, t=time_index, at='translate')
                            #cmds.setKeyframe( at='translate', itt='spline', ott='spline', al=al )
                except IndexError:
                    print(IndexError.message)
                try:
                    bone_frames = len(bone.rotationFrames)
                    total_frames = animData.numFrames
                    frame_skip = round(float(total_frames)/float(bone_frames))
                    frame_array = [frame_skip*n for n in range(0,bone_frames)]
                    frame_quat_prev = False
                    if float(fi) in frame_array:
                        frame_quat = bone.rotationFramesQuat[frame_array.index(fi)]
                        #MIMIC POSES DON'T GET INVERTED
                        if type is "face":
                            # cmds.xform( ro=(-bone.rotationFrames[frame_array.index(fi)][0],
                            #                 -bone.rotationFrames[frame_array.index(fi)][1],
                            #                 -bone.rotationFrames[frame_array.index(fi)][2]))
                            xform.setRotation(frame_quat.invertIt(), om.MSpace.kObject)
                        else:
                            ## temp solution to blend face animations on top of current animations
                            ## maybe create a new animLayer if this is the case
                            ## could get messy without a bind pose
                            ## an animLayer based off the bind pose could work so there is something to export.
                            ## exports of face animation will be borken in-game if exported as-is.
                            if face_animation:
                                xform.rotateBy(frame_quat, om.MSpace.kObject)
                            else:
                                xform.setRotation(frame_quat, om.MSpace.kObject)
                        # if type is "face":
                        #     cmds.xform( ro=(bone.rotationFrames[frame_array.index(fi)][0],
                        #                     bone.rotationFrames[frame_array.index(fi)][1],
                        #                     bone.rotationFrames[frame_array.index(fi)][2]))
                        # else:
                        #     cmds.xform( ro=(-bone.rotationFrames[frame_array.index(fi)][0],
                        #                     -bone.rotationFrames[frame_array.index(fi)][1],
                        #                     -bone.rotationFrames[frame_array.index(fi)][2]))
                        #cmds.setKeyframe( at='rotate', itt='auto', ott='auto', al=al )
                        if al:
                            pm.setKeyframe(boneName, t=time_index, at='rotate', al=al, minimizeRotation=True, itt='linear', ott='linear')
                        else:
                            pm.setKeyframe(boneName, t=time_index, at='rotate', minimizeRotation=True, itt='linear', ott='linear')
                        ## temp solution to blend face animations
                        ## restore the orignal frame after every rotateBy keyframe
                        if face_animation:
                            xform.setRotation(orig_rotation, om.MSpace.kObject)
                except IndexError:
                    print(IndexError.message)

        if animData.tracks:
            for track in animData.tracks:
                trackname = scene_actor+"_"+track.trackName
                if pm.animLayer(trackname, query=True, ex=True):
                    try:
                        track_frames = len(track.trackFrames)
                        total_frames = animData.numFrames
                        frame_skip = round(float(total_frames)/float(track_frames))
                        frame_array = [frame_skip*n for n in range(0,track_frames)]
                        if float(fi) in frame_array:
                            weight = round(track.trackFrames[frame_array.index(fi)], 5)
                            pm.select(trackname)
                            pm.animLayer( trackname, edit=True, weight= weight * global_weight)
                            pm.setKeyframe( trackname, attribute='weight', t=time_index )

                            #cmds.setKeyframe( at='translate', itt='spline', ott='spline', al=al )
                    except IndexError:
                        pass
                        # handle this


def loadSkeletalAnimationSetFile(filename):
    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.json'):
        with open(filename) as file:
            return read_json_w3.Read_CSkeletalAnimationSet(json.loads(file.read()))
    else:
        return None

def import_w3_animSet(filename):
    CSkeletalAnimationSet = loadSkeletalAnimationSetFile(filename)
    return CSkeletalAnimationSet
