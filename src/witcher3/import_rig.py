from maya import cmds

import copy
import operator
import os
import re
import json
import read_json_w3
reload(read_json_w3)
import fbx_util
reload(fbx_util)
import anims
reload(anims)
from math import degrees
from math import radians
import maya.api.OpenMaya as om
import maya.OpenMaya as OpenMaya
import pymel.core as pm
import maya.mel as mel

def loadW3File(filename):
    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.json'):
        w3Data = read_json_w3.readCSkeleton(filename)
    else:
        w3Data = None

    return w3Data

def import_w3_rig(filename, ns="ciri"):
    print("Importing file: ", filename)
    w3Data = loadW3File(filename)
    if not w3Data:
        return '{NONE}'
    else:
        return import_w3_rig2(w3Data, ns)

def import_w3_rig2(w3Data,ns="ciri"):
    currentNs = cmds.namespaceInfo(cur=True)
    cmds.namespace(relativeNames=True)
    if not cmds.namespace(ex=':%s'%ns):
        cmds.namespace(add=':%s'%ns)
    cmds.namespace(set=':%s'%ns)

    for bone in w3Data.bones:
        cmds.select( d=True )
        if not cmds.objExists(bone.name):
            cmds.joint( name=bone.name, p=(float(bone.co[0]),float(bone.co[1]),float(bone.co[2])), rad=0.01 )
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
    cmds.namespace(set=currentNs)
    cmds.namespace(relativeNames=False)
    #get a list of root bones to return, these need to be groups and scaled to attach to mesh
    root_bones=[]
    for bone in w3Data.bones:
        if bone.parentId == -1:
            root_bones.append(ns+":"+bone.name)
    return root_bones;

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


def _getHierarchyRootJoint( joint="" ):
    rootJoint = joint
    while (True):
        parent = pm.listRelatives( rootJoint,
                                     parent=True,
                                     type='joint' )
        if not parent:
            break;
        rootJoint = parent[0]
    return rootJoint



def constrain_w3_rig(source, target, mo=False):
    #attach source to target
    #any bone in the source attaches to target
    root_constrained = False
    if not pm.namespace( exists=source ):
        return
    #get all bones in source
    source = source+":*"
    pm.select( source,  r=1, hi=1 )
    #TODO FIND A WAY TO MOVE MESH INTO POSITION BEFORE DOING A CONSTRAIN WITH MAINTAIN OFFEST
    #USING THE ROOT OF HI SHOULD WORK
    bones = pm.ls( selection=True, type="joint" )

    root_bones=[]
    for bone in bones:
        if _getHierarchyRootJoint(bone.getName()) in root_bones:
            pass
        else:
            print(_getHierarchyRootJoint(bone.getName()))
            root_bones.append(_getHierarchyRootJoint(bone.getName()))
    # root = _getHierarchyRootJoint(bones[0].getName())
    # pm.select( root, hi=1 )
    # bones = pm.ls( selection=True, type="joint" )

    #loop those bones
    for joint in bones:
        bone_name = joint.getName().split(':')[-1]
        if pm.objExists("{}:{}".format(target,bone_name)):
            # root_constrain = False
            # for rb in root_bones:
            #     if bone_name == rb.split(':')[-1]:
            #         root_constrain = True
            if "eye" in bone_name or "ear" in bone_name:
                pm.parentConstraint( joint.getName(), "{}:{}".format(target,bone_name), mo=True )
            else:
                pm.parentConstraint( joint.getName(), "{}:{}".format(target,bone_name) )

def hard_attach(source, target, mo=False):
    pm.parentConstraint( source, target, mo=True )

def import_w3_animation_OLD(w3Data, SkeletalAnimation, type, al=False):
    bone_frames = {}
    for rig_bone in w3Data.bones:
        bone_frames[rig_bone.name]={
            "positionFrames":[],
            "rotationFrames":[],
            "scaleFrames":[]
        }
    animData = SkeletalAnimation.animBuffer
    multipart = False
    if animData.parts:
        multipart=True

    # start time of playback
    #cmds.playbackOptions(q= 1, min= 1)
    # end time of playback
    #cmds.playbackOptions(q= 1, max= animData.numFrames, aet=animData.numFrames)
    cmds.playbackOptions( min='1', max=str(animData.numFrames), ast='1', aet=str(animData.numFrames))
    # start time of playback
    start = 1 #cmds.playbackOptions(q= 1, min= 1)
    # end time of playback
    end = animData.numFrames+1#cmds.playbackOptions(q= 1, max= 1)
    for fi in range(int(start), int(end)):
        time_index=fi
        fi=fi-1
        # move frame
        #cmds.currentTime(i, e= 1)
        # for bone in animData.bones:

        #     ## NEED TO CHECK DT AND SKIP PROPER FRAMES
        #     if cmds.objExists(bone.BoneName):
        #         cmds.select(bone.BoneName);
        #         sel_list = om.MSelectionList()
        #         sel_list.add(bone.BoneName)
        #         obj = sel_list.getDependNode(0)
        #         xform = om.MFnTransform(obj)
        #         try:
        #             bone_frames = len(bone.positionFrames)
        #             total_frames = animData.numFrames
        #             frame_skip = round(float(total_frames)/float(bone_frames))
        #             frame_array = [frame_skip*n for n in range(0,bone_frames)]
        #             if float(fi) in frame_array:
        #                 cmds.xform( t=(bone.positionFrames[frame_array.index(fi)][0],
        #                                 bone.positionFrames[frame_array.index(fi)][1],
        #                                 bone.positionFrames[frame_array.index(fi)][2]))
        #                 if al:
        #                     pm.setKeyframe(bone.BoneName, t=time_index, at='translate', al=al)
        #                 else:
        #                     pm.setKeyframe(bone.BoneName, t=time_index, at='translate')
        #                 #cmds.setKeyframe( at='translate', itt='spline', ott='spline', al=al )
        #         except IndexError:
        #             pass
        #             # handle this
        #         try:
        #             bone_frames = len(bone.rotationFrames)
        #             total_frames = animData.numFrames
        #             frame_skip = round(float(total_frames)/float(bone_frames))
        #             frame_array = [frame_skip*n for n in range(0,bone_frames)]
        #             if float(fi) in frame_array:
        #                 #MIMIC POSES DON'T GET INVERTED
        #                 if type is "face":
        #                     cmds.xform( ro=(-bone.rotationFrames[frame_array.index(fi)][0],
        #                                     -bone.rotationFrames[frame_array.index(fi)][1],
        #                                     -bone.rotationFrames[frame_array.index(fi)][2]))
        #                 else:
        #                     xform.setRotation(bone.rotationFramesQuat[frame_array.index(fi)], om.MSpace.kObject)
        #                 # if type is "face":
        #                 #     cmds.xform( ro=(bone.rotationFrames[frame_array.index(fi)][0],
        #                 #                     bone.rotationFrames[frame_array.index(fi)][1],
        #                 #                     bone.rotationFrames[frame_array.index(fi)][2]))
        #                 # else:
        #                 #     cmds.xform( ro=(-bone.rotationFrames[frame_array.index(fi)][0],
        #                 #                     -bone.rotationFrames[frame_array.index(fi)][1],
        #                 #                     -bone.rotationFrames[frame_array.index(fi)][2]))
        #                 #cmds.setKeyframe( at='rotate', itt='auto', ott='auto', al=al )
        #                 if al:
        #                     pm.setKeyframe(bone.BoneName, t=time_index, at='rotate', al=al)
        #                 else:
        #                     pm.setKeyframe(bone.BoneName, t=time_index, at='rotate')
        #         except IndexError:
        #             pass
        for track in animData.tracks:
            ns= "ciri_"
            trackname = ns+track.trackName
            if pm.animLayer(trackname, query=True, ex=True):
                try:
                    track_frames = len(track.trackFrames)
                    total_frames = animData.numFrames
                    frame_skip = round(float(total_frames)/float(track_frames))
                    frame_array = [frame_skip*n for n in range(0,track_frames)]
                    if float(fi) in frame_array:
                        weight = round(track.trackFrames[frame_array.index(fi)], 5)
                        pm.select(trackname)
                        pm.animLayer( trackname, edit=True, weight= weight)
                        pm.setKeyframe( trackname, attribute='weight', t=time_index )

                        #cmds.setKeyframe( at='translate', itt='spline', ott='spline', al=al )
                except IndexError:
                    pass
                    # handle this
    return SkeletalAnimation

def loadFaceFile(filename):
    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.json'):
        faceData = read_json_w3.readFaceFile(filename)
    else:
        faceData = None

    return faceData

def import_w3_face(filename):
    #load skeleton for face using import_w3_rig
    faceData = loadFaceFile(filename)
    mimicSkeleton = import_w3_rig2(faceData.mimicSkeleton)
    #floatTrackSkeleton = import_w3_rig2(faceData.floatTrackSkeleton)

    #TODO create checkbox to select what to import
    #mimicPoses = import_w3_mimicPoses(faceData.mimicPoses, faceData.mimicSkeleton)
    #load the mimicPoses as keyframe 0 poses each with anim layer
    return mimicSkeleton

def export_w3_face(filename):
    pass

def import_w3_mimicPoses(poses, mimicSkeleton, actor, mimic_namespace):
    # ns = "ciri"
    # if not pm.namespace( exists=ns ):
    #     pm.namespace( add=ns )
    # ns = ns+":"
    # root_ctrl = None
    # try:
    #     root_ctrl = pm.PyNode('torso3')
    # except:
    #     root_ctrl = pm.PyNode(ns + 'torso3')

    ##create the layers 
    for pose in poses:
        # if pose.name == 'lips_blow':
        #   break
        if not pm.animLayer(actor+"_"+pose.name, ex=True, q=True):
            pm.animation.animLayer(actor+"_"+pose.name, weight=0.0)

    for pose in poses:
        # if pose.name == 'lips_blow':
        #   break
        animBuffer = pose.animBuffer
        select_list= [] #select only the bones moved by the pose.

        for bone in animBuffer.bones:
            all_zeros = bone.positionFrames[0].count(0.0)
            all_zerosQ = bone.rotationFrames[0].count(0.0)
            if bone.positionFrames[0].count(0.0) is 3 and bone.rotationFrames[0].count(0.0) is 3:
                pass
            else:
                select_list.append(mimic_namespace+":"+bone.BoneName)
        pm.select(select_list)
        pm.animation.animLayer(actor+"_"+pose.name, edit=True, addSelectedObjects=True)
        anims.import_w3_animation2(pose, mimic_namespace, "face", actor+"_"+pose.name)
