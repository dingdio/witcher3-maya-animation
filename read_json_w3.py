
import json
from . import w3_types
reload(w3_types)
import maya.api.OpenMaya as om
from maya import cmds
from math import degrees
from math import radians

def readXYZ(file):
    x = file["X"]  # X pos
    y = file["Y"]  # Y pos
    z = file["Z"]  # Z pos
    coords = [x, y, z]
    return coords

def readxyz(file):
    x = file["x"]  # X pos
    y = file["y"]  # Y pos
    z = file["z"]  # Z pos
    coords = [x, y, z]
    return coords

def readEulerXYZ(file):
    x = degrees((file.x))  # X pos
    y = degrees((file.y))  # y pos
    z = degrees((file.z))  # z pos
    coords = [x, y, z]
    return coords

    
def deg_to_rad_XYZ(file):
    x = radians(file[0])  # X pos
    y = radians(file[1])  # y pos
    z = radians(file[2])  # z pos
    coords = [x, y, z]
    return coords


def readXYZW(file):
    x = file["X"]  # X pos
    y = file["Y"]  # Y pos
    z = file["Z"]  # Z pos
    w = file["W"]  # Z pos
    coords = [x, y, z, w]
    return coords

def readBones(file):
    bones = []
    # Bone Count
    boneCount = len(file["names"])
    for boneId in range(boneCount):
        boneName = file["names"][boneId]
        parentId = file["parentIdx"][boneId]
        coords = readXYZ(file["positions"][boneId])
        scale = readXYZ(file["scales"][boneId])
        quat_read = readXYZW(file["rotations"][boneId])
        quat = om.MQuaternion( quat_read[0],quat_read[1],quat_read[2],-quat_read[3] )
        quat.normalizeIt()
        euler = quat.asEulerRotation()
        e = euler.reorderIt(5)

        ro = readEulerXYZ(e)

        w3Bone = w3_types.W3Bone(boneId, boneName, coords, parentId, ro, quat, scale)
        bones.append(w3Bone)
    return bones


def eularToQuat(file):
    rot_rad = deg_to_rad_XYZ(file)
    euler = om.MEulerRotation( rot_rad[0],rot_rad[1],rot_rad[2], 5 )
    quat = euler.asQuaternion()
    rot = [quat.x,quat.y,quat.z,quat.w]
    return rot

def readW3Data(filename):
    with open(filename) as file:
        data = file.read()
        ioStream = json.loads(data)
    print('Reading Bones')
    bones = readBones(ioStream)
    hasBones = bool(bones)
    #print('Reading Meshes')
    #meshes = readMeshes(ioStream, hasBones)
    w3ModelData = w3_types.W3Data(bones=bones, json=ioStream)
    return w3ModelData



def readAnimation(file):
    bones = []
    # Bone Count
    boneCount = len(file)
    for boneId in range(boneCount):
        boneName = file[boneId]['BoneName']
        positionFrames=[]
        rotationFrames=[]
        #rotationFramesQuat=[]
        scaleFrames=[]

        posFramesArr = file[boneId]['positionFrames']
        for frameId in range(len(posFramesArr)):
            positionFrames.append(readxyz(posFramesArr[frameId]))

        scaleFramesArr = file[boneId]['scaleFrames']
        for frameId in range(len(scaleFramesArr)):
            scaleFrames.append(readxyz(scaleFramesArr[frameId]))

        rotFramesArr = file[boneId]['rotationFrames']
        for frameId in range(len(rotFramesArr)):
            quat_read = readXYZW(rotFramesArr[frameId])
            quat = om.MQuaternion(quat_read[0],quat_read[1],quat_read[2],-quat_read[3] )
            # euler = quat.asEulerRotation()
            # e = euler.reorderIt(5)
            # ro = readEulerXYZ(e)
            # rotationFrames.append(ro)
            quat.normalizeIt()
            rotationFrames.append(quat)

        frames = w3_types.w2AnimsFrames(boneId,
                        BoneName = file[boneId]['BoneName'],
                        position_dt = file[boneId]['position_dt'],
                        position_numFrames = file[boneId]['position_numFrames'],
                        positionFrames = positionFrames,
                        rotation_dt = file[boneId]['rotation_dt'],
                        rotation_numFrames = file[boneId]['rotation_numFrames'],
                        rotationFrames = rotationFrames,
                        scale_dt = file[boneId]['scale_dt'],
                        scale_numFrames = file[boneId]['scale_numFrames'],
                        scaleFrames = scaleFrames)
        bones.append(frames)
    return bones

def readAnimFile(filename):
    with open(filename) as file:
        data = file.read()
        animJson = json.loads(data)
    print('Reading Animation')
    bones = readAnimation(animJson['bones'])
    hasBones = bool(bones)
    name = animJson['name']
    duration = animJson['duration']
    numFrames = animJson['numFrames']
    dt = animJson['dt']
    w3AnimlData = w3_types.w2AnimsData(name = name,
                                        duration = duration,
                                        numFrames = numFrames,
                                        dt = dt,
                                        bones=bones,
                                        json=animJson)
    return w3AnimlData