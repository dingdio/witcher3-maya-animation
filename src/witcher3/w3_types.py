# <pep8 compliant>


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

class W3Data:

    def __init__(self, bones=[], json=[]):
        self.bones = bones
        self.json = json

class w2AnimsData:
    def __init__(self, name ="", duration=0.0, numFrames= 0, dt=0.0333333351, bones=[], json=[]):
        self.name = name
        self.duration = duration
        self.numFrames = numFrames
        self.dt = dt
        self.bones = bones
        self.json = json