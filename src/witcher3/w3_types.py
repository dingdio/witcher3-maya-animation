# <pep8 compliant>
import re
import read_json_w3
reload(read_json_w3)

class W3Bone:

    def __init__(self, id, name, co, parentId, ro, ro_quat, sc):
        self.id = id
        self.name = name
        self.co = co
        self.ro = ro
        self.ro_quat = ro_quat
        self.sc = sc
        self.parentId = parentId

class w2AnimsFrames: 
    def __init__(self,
                id,
                BoneName,
                position_dt,
                position_numFrames,
                positionFrames,
                rotation_dt,
                rotation_numFrames,
                rotationFrames,
                scale_dt,
                scale_numFrames,
                scaleFrames,
                rotationFramesQuat):
        self.id = id
        self.BoneName = BoneName
        self.position_dt = position_dt
        self.position_numFrames = position_numFrames
        self.positionFrames = positionFrames
        self.rotation_dt = rotation_dt
        self.rotation_numFrames = rotation_numFrames
        self.rotationFrames = rotationFrames
        self.scale_dt = scale_dt
        self.scale_numFrames = scale_numFrames
        self.scaleFrames = scaleFrames
        self.rotationFramesQuat = rotationFramesQuat

class CSkeleton:
    def __init__(self, bones=[]):
        self.bones = bones

class SCutsceneActorDef:
    def __init__(self,  tag,
                        name,
                        type,
                        template,
                        useMimic,
                        voiceTag):
        self.tag = tag
        self.name = name
        self.template = template
        self.useMimic = useMimic
        self.type = type
        self.voiceTag = voiceTag
    @classmethod
    def from_json(cls, data):
        return cls(**data)

class CSkeletalAnimationSet:
    def __init__(self, animations=[]):
        self.animations = animations
    @classmethod
    def from_json(cls, data):
        animations = list(map(CSkeletalAnimationSetEntry.from_json, data["animations"]))
        return cls(animations)

class CCutsceneTemplate:
    def __init__(self, animations=[], SCutsceneActorDefs=[]):
        self.animations = animations
        self.SCutsceneActorDefs = SCutsceneActorDefs
    @classmethod
    def from_json(cls, data):
        SCutsceneActorDefs = list(map(SCutsceneActorDef.from_json, data["SCutsceneActorDefs"]))
        animations = list(map(CSkeletalAnimationSetEntry.from_json, data["animations"]))
        return cls(animations, SCutsceneActorDefs)

class CSkeletalAnimationSetEntry:
    def __init__(self, animation="", entries=[]):
        self.animation = animation
        self.entries = entries
    @classmethod
    def from_json(cls, data):
        data["animation"] = CSkeletalAnimation.from_json(data["animation"])
        return cls(**data)

class CSkeletalAnimation:
    def __init__(self, name ="", duration=0.0, framesPerSecond=30, animBuffer=[], motionExtraction={}):
        self.name = name
        self.duration = duration
        self.framesPerSecond = framesPerSecond
        self.animBuffer = animBuffer
        self.motionExtraction = motionExtraction
    @classmethod
    def from_json(cls, data):
        if 'parts' in data["animBuffer"]:
            animBuffer = CAnimationBufferMultipart.from_json(data["animBuffer"])
        else:
            animBuffer = CAnimationBufferBitwiseCompressed.from_json(data["animBuffer"])
        data["animBuffer"] = animBuffer
        return cls(**data)

class CAnimationBufferBitwiseCompressed:
    def __init__(self, bones=[], tracks=[], duration=0.0, numFrames=0, dt=0.0333333351, version = 0):
        self.bones = bones
        self.tracks = tracks
        self.duration = duration
        self.numFrames = numFrames
        self.dt = dt
        self.version = version
    @classmethod
    def from_json(cls, data):
        data["bones"] = read_json_w3.readAnimation(data["bones"])
        if data.get("tracks", []):
            data["tracks"] = read_json_w3.readTracks(data["tracks"])
        return cls(**data)

class CAnimationBufferMultipart:
    def __init__(self, numFrames=0,numBones=0, numTracks=0, firstFrames=[], parts=[] ):
        self.numFrames = numFrames
        self.numBones = numBones
        self.numTracks = numTracks
        self.firstFrames = firstFrames
        self.parts = parts
    @classmethod
    def from_json(cls, data):
        parts = list(map(CAnimationBufferBitwiseCompressed.from_json, data["parts"]))
        data["parts"] = parts
        return cls(**data)

class CMimicFace:
    def __init__(self, name="", mimicSkeleton = [], floatTrackSkeleton = [], mimicPoses=[]):
        self.name = name
        self.mimicSkeleton = mimicSkeleton
        self.floatTrackSkeleton = floatTrackSkeleton
        self.mimicPoses = mimicPoses

class Track: 
    def __init__(self,
                id,
                trackName,
                numFrames,
                dt,
                trackFrames):
        self.id = id
        self.trackName = trackName
        self.numFrames = numFrames
        self.dt = dt
        self.trackFrames = trackFrames


class Entity: 
    def __init__(self,
                name="default_name",
                animation_rig = "none",
                includedTemplates = [],
                staticMeshes = {}):
        self.name = name
        self.animation_rig = animation_rig
        self.includedTemplates = includedTemplates
        self.staticMeshes = staticMeshes