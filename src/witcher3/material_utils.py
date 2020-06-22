import os
from maya import cmds
import pymel.core as pm

#texture_folder = "F:\\FF7_Remake\\End\\Content\\GameContents\\Character\\Player\\PC0000_00_Cloud_Standard\\Texture\\"


def import_material(mat_name, model_path):
    texture_folder= model_path+"Texture\\"
    filename= model_path+"Material\\"+mat_name

    dirpath, file = os.path.split(filename)
    basename, ext = os.path.splitext(file)
    if ext.lower() in ('.mat'):
        #create arnold material
        print(basename)
        file = open(filename, "r")
        for line in file:
            tex_name = line.split('=')[1].rstrip()
            tex_type = line.split('=')[0]
            print(tex_name)
            print(tex_type)
            assignMat(tex_name, basename, texture_folder)
            #search and assign textures
    files = cmds.ls(type='file')
    for f in files:
        if "Diffuse" in f:
            cmds.setAttr(f + '.colorSpace', 'sRGB', type='string')

def assignMat(texture_name = "PC0000_00_BodyB_C", material_name = "PC0000_00_Pants", texture_folder=""):
    material = pm.ls(material_name)
    if material:
        material = material[0]
        specularRoughness = '%s.specularRoughness' % material
        specularColor = '%s.specularColor' % material
        coatColor = '%s.coatColor' % material
        coatWeight = '%s.coat' % material
        print(material.getName())
        fileNode = material.connections(type='file')
        if fileNode and "_C" in texture_name:
            for file in fileNode:
                fileOutColor = '%s.outColor' % file
                #pm.connectAttr(sphereR, coneR)
                if pm.isConnected( fileOutColor, specularColor ):
                    pm.disconnectAttr(fileOutColor, specularColor)
                if pm.isConnected( fileOutColor, coatColor ):
                    pm.disconnectAttr(fileOutColor, coatColor)
                pm.setAttr(file.fileTextureName, texture_folder+texture_name+".tga")
                textureFile = pm.getAttr(file.fileTextureName)
                print 'This is the file', str(textureFile)
                #create_hair(g, material, file, mat_name)
        bumpNode = material.connections(type='bump2d')
        if bumpNode and "_N" in texture_name:
            bumpNode= bumpNode[0]
            print(pm.getAttr(bumpNode.bumpValue))
            fileNode = bumpNode.connections(type='file')
            for file in fileNode:
                pm.setAttr(file.fileTextureName, texture_folder+texture_name+".tga")
                textureFile = pm.getAttr(file.fileTextureName)
                print 'This is the file', str(textureFile)
                #create_hair(g, material, file, mat_name)

        #set values for material
        pm.setAttr(specularColor, (1.0, 1.0, 1.0))
        pm.setAttr(specularRoughness, 0.5)
        pm.setAttr(coatWeight, 0.0)

