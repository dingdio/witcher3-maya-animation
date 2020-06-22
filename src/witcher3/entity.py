
import os
import re
from maya import cmds
import pymel.core as pm
import import_rig
reload(import_rig)

import read_json_w3
reload(read_json_w3)
import fbx_util
reload(fbx_util)

def repo_file(filepath):
    repo = "D:/Witcher_uncooked_clean/raw_ent/"
    return repo+filepath

def fixed(entity):
    entity.animation_rig = repo_file(entity.animation_rig)+".json";

    for template in entity.includedTemplates:
        for chunk in template['chunks']:
            if "mesh" in chunk:
                chunk['mesh'] = repo_file(chunk['mesh'].replace(".w2mesh", "_CONVERT_.fbx"))
            if "skeleton" in chunk:
                chunk['skeleton'] = repo_file(chunk['skeleton'])+".json"
            if "dyng" in chunk:
                chunk['dyng'] = repo_file(chunk['dyng'])+".json"
            if "mimicFace" in chunk:
                chunk['mimicFace'] = repo_file(chunk['mimicFace'])+".json"
    if entity.staticMeshes:
        for chunk in entity.staticMeshes.get('chunks', []):
            if "mesh" in chunk:
                chunk['mesh'] = repo_file(chunk['mesh'].replace(".w2mesh", "_CONVERT_.fbx"))
    return entity

def isChildNode(chunkIndex, templateChunks):
    for chunk in templateChunks:
        if "child" in chunk and chunk['child'] == chunkIndex:
            return True
    return False

def GetChunkNS(chunkIndex, templateChunks, index):
    for chunk in templateChunks:
        if chunk['chunkIndex'] == chunkIndex:
            return chunk['type']+str(index)+str(chunk['chunkIndex'])

def import_ent(filename, load_face_poses):
    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.json'):
        entity = read_json_w3.readEntFile(filename)
    else:
        entity = None
    ent_namespace = entity.name+":"

    entity = fixed(entity)

    root_bone = import_rig.import_w3_rig(entity.animation_rig, entity.name)
    animation_rig = root_bone
    group = pm.group(n=entity.name+"_anim_skel", em=True )
    pm.parent(animation_rig,group)
    pm.select(group)
    pm.xform( ro=(90,0,180), s=(100,100,100) )
    pm.addAttr( longName="witcher_name", dt="string" )
    pm.setAttr( group+'.witcher_name', entity.name )

    mimic_rig = False
    mimic_namespace = False
    rig_rig = False
    faceData = False
    constrains = []
    HardAttachments = []
    hair_meshes = []
    eye_meshes = []

    #for template in entity.includedTemplates:
    for i in range(len(entity.includedTemplates)):
        cur_chunks = entity.includedTemplates[i]['chunks']
        for chunk in cur_chunks:
            #each chunk gets it's own namespace as each "CMeshComponent" has lods and materials with the same name
            # ENTITY_NAMESPACE + TYPE + TEMPLATE_INDEX + CHUNK_INDEX
            chunk_namespace = ent_namespace+chunk['type']+str(i)+str(chunk['chunkIndex'])
            if not isChildNode(chunk['chunkIndex'], cur_chunks):
                constrains.append([entity.name, chunk_namespace])
            if chunk['type'] == "CMeshSkinningAttachment" or chunk['type'] == "CAnimatedAttachment":
                parent = chunk['parent']
                child = chunk['child']
                for findChunk in cur_chunks:
                    if findChunk['chunkIndex'] == parent:
                        if findChunk['type'] == "CAnimDangleComponent":
                            parentNS = GetChunkNS(findChunk['constraint'], cur_chunks, i)
                        else:
                            parentNS = findChunk['type']+str(i)+str(parent)
                    if findChunk['chunkIndex'] == child:
                        if findChunk['type'] == "CAnimDangleComponent":
                            childNS = GetChunkNS(findChunk['constraint'], cur_chunks, i)
                        else:
                            childNS = findChunk['type']+str(i)+str(child)
                if parentNS and childNS:
                    print([parentNS, childNS])
                    constrains.append([ent_namespace+parentNS, ent_namespace+childNS])
                else:
                    print("ERROR FINDING SKINNING ATTACHMENT")
            if "mesh" in chunk:
                fbx_name = fbx_util.importFbx(chunk['mesh'], chunk['type']+str(i)+str(chunk['chunkIndex']), entity.name)
                if "\\he_" in chunk['mesh']:
                    eye_meshes.append(chunk_namespace)
                if "\\c_" in chunk['mesh'] or "\\hh_" in chunk['mesh'] or "\\hb_" in chunk['mesh']:
                    hair_meshes.append(chunk_namespace)
            if "skeleton" in chunk:
                rig_grp_name = entity.name+chunk['type']+"_rig"+"_grp"
                root_bone = import_rig.import_w3_rig(chunk['skeleton'],chunk_namespace)
                group = pm.group(n=rig_grp_name, em=True )
                pm.parent(root_bone,group)
                pm.select(group)
                pm.xform( ro=(90,0,180), s=(100,100,100) )
                rig_rig= root_bone

            if "dyng" in chunk:
                rig_grp_name = entity.name+chunk['type']+"_rig"+"_grp"
                root_bone = import_rig.import_w3_rig(chunk['dyng'],chunk_namespace)
                group = pm.group(n=rig_grp_name, em=True )
                pm.parent(root_bone,group)
                pm.select(group)
                pm.xform( ro=(90,0,180), s=(100,100,100) )

            if "mimicFace" in chunk:
                rig_grp_name = entity.name+chunk['type']+"_rig"+"_grp"
                #root_bone = import_rig.import_w3_rig(chunk['rig'],chunk_namespace)
                faceData = import_rig.loadFaceFile(chunk['mimicFace'])
                root_bone = import_rig.import_w3_rig2(faceData.mimicSkeleton,chunk_namespace)
                group = pm.group(n=rig_grp_name, em=True )
                pm.parent(root_bone,group)
                pm.select(group)
                pm.xform( ro=(90,0,180), s=(100,100,100) )
                mimic_rig= root_bone
                mimic_namespace = chunk_namespace
        if "camera" in entity.includedTemplates[i]:
            currentNs = cmds.namespaceInfo(cur=True)
            cmds.namespace(relativeNames=True)
            if not cmds.namespace(ex=':%s'%entity.name):
                cmds.namespace(add=':%s'%entity.name)
            cmds.namespace(set=':%s'%entity.name)
            camera = pm.camera(name="w_cam")
            pm.parent( camera, "Camera_Node" )
            pm.xform( ro=(90, 0, 0), s=(0.2,0.2,0.2), t=(0, 0, 0) )
            cmds.namespace(set=currentNs)
            cmds.namespace(relativeNames=False)

    if entity.staticMeshes is not None:
        cur_chunks = entity.staticMeshes.get('chunks', [])
        i = ""
        for chunk in cur_chunks:
            #each chunk gets it's own namespace as each "CMeshComponent" has lods and materials with the same name
            # ENTITY_NAMESPACE + TYPE + TEMPLATE_INDEX + CHUNK_INDEX
            chunk_namespace = ent_namespace+chunk['type']+str(i)+str(chunk['chunkIndex'])
            if not isChildNode(chunk['chunkIndex'], cur_chunks):
                constrains.append([entity.name, chunk_namespace])
            if "mesh" in chunk:
                fbx_name = fbx_util.importFbx(chunk['mesh'], chunk['type']+str(i)+str(chunk['chunkIndex']), entity.name)
                if "\\he_" in chunk['mesh']:
                    eye_meshes.append(chunk_namespace)
                if "\\c_" in chunk['mesh'] or "\\hh_" in chunk['mesh'] or "\\hb_" in chunk['mesh']:
                    hair_meshes.append(chunk_namespace)
            if chunk['type'] == "CHardAttachment":
                parent = chunk['parent']
                child = chunk['child']
                parentSlotName = chunk['parentSlotName']
                parentSlot = chunk['parentSlot']
                for findChunk in cur_chunks:
                    if findChunk['chunkIndex'] == child:
                        childNS = findChunk['type']+str(i)+str(child)+":Mesh_lod0"
                if parentSlotName and childNS:
                    print([parentSlotName, childNS])
                    HardAttachments.append([ent_namespace+parentSlotName, ent_namespace+childNS])
                else:
                    print("ERROR FINDING SKINNING ATTACHMENT")

    # main_group = pm.group(n=entity.name+"_grp", em=True )
    # pm.parent(fbx_name,main_group)
    pm.modelEditor( 'modelPanel4', e=True, displayTextures=True )
    pm.modelEditor( 'modelPanel4', e=True, twoSidedLighting=True )

    #SET PROPER COLOR SPACE
    files = cmds.ls(type='file')
    for f in files:
        print(f)
        if "Normal" in f:
            cmds.setAttr(f + '.colorSpace', 'Raw', type='string')
        if "Diffuse" in f:
            cmds.setAttr(f + '.colorSpace', 'sRGB', type='string')

    # Set "Tangent Space" Coordinate Systems "Left Handed"
    allMesh = pm.ls(type='mesh')
    for mesh in allMesh:
        mesh.tangentSpace.set(2)
        sg = mesh.outputs(type='shadingEngine')
        for g in sg:
            for material in g.surfaceShader.listConnections():
                if "diffuse" in material:
                    material.diffuse.set(1.0)
        #GET SHADERS
        #check textures
        #do material operations
        if inList(mesh.nodeName(), eye_meshes) and not mesh.nodeName().endswith("Orig"):
            print(mesh)
            #Get the shading group from the selected mesh
            sg = mesh.outputs(type='shadingEngine')
            #print(sg)

            for g in sg:
                #sgInfo = g.connections(mat=True)
                for material in g.surfaceShader.listConnections():
                    #print(material)
                    fileNode = material.connections(type='file')
                    if fileNode:
                        for file in fileNode:
                            textureFile = pm.getAttr(file.fileTextureName)
                            if "eyelash" in textureFile:
                                mat_name = material.getName()
                                print("found eyelash on "+mat_name)
                                pm.rename(mat_name, mat_name+"_OLD")
                                eyelash = create_hair(g, material, file, mat_name)
                                eyelash.Diffuse.set(1.0)
                                eyelash.AmbiantAmount.set(0.0)
                                eyelash.OpacityAmount.set(0.8)
                                #print 'This is the file', str(textureFile)
                    else:
                        if set(material.color.get()) == set([1.0, 1.0, 1.0]):
                            material.transparency.set([1.0, 1.0, 1.0, 1.0])

        if inList(mesh.nodeName(), hair_meshes) and not mesh.nodeName().endswith("Orig"):
            print(mesh)
            #Get the shading group from the selected mesh
            sg = mesh.outputs(type='shadingEngine')
            #print(sg)

            for g in sg:
                #sgInfo = g.connections(mat=True)
                for material in g.surfaceShader.listConnections():
                    print(material)
                    mat_name = material.getName()
                    pm.rename(mat_name, mat_name+"_OLD")
                    fileNode = material.connections(type='file')
                    if fileNode:
                        for file in fileNode:
                            textureFile = pm.getAttr(file.fileTextureName)
                            print 'This is the file', str(textureFile)
                            create_hair(g, material, file, mat_name)
    # allShader = pm.ls(type='shader')
    # for shade in allShader:
    #     shade.diffuse.set(1.000)

    for constrain in constrains:
        #print(constrain)
        import_rig.constrain_w3_rig(constrain[0], constrain[1], mo=False)

    for constrain in HardAttachments:
        import_rig.hard_attach(constrain[0], constrain[1], mo=False)

    if load_face_poses:
        mimicPoses = import_rig.import_w3_mimicPoses(faceData.mimicPoses, faceData.mimicSkeleton, actor=entity.name, mimic_namespace=mimic_namespace)
    return ''#filename+"Cake"


def inList(name, mylist):
    for el in mylist:
        if el in name:
            return True
    return False
#witcher3.world()
##UTIL FUNCTIONS
def create_hair(g, material, textureFile, mat_name):
    hairNode = pm.shadingNode('ShaderfxShader', asShader=True, name=mat_name)
    dirpath, file = os.path.split(import_rig.__file__)
    graph_file = directory = dirpath+"\\ShaderFX\\witcher_3_hair.sfx"
    pm.other.shaderfx(sfxnode=hairNode, loadGraph=graph_file)

    hairNode.outColor >> g.surfaceShader
    textureFile.fileTextureName >> hairNode.OpacityMap
    return hairNode