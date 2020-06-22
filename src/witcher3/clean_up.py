# filename = "D://Witcher_uncooked_modkit/base_rig_anim_export/import_rig.py"
# exec(compile(open(filename).read(), filename, 'exec'))



import bpy

bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['Mesh_lod1'].select = True
bpy.ops.object.delete() 

for lod in range(0,9):
    
    pass


#BONE CLEAN
import bpy
import os
import json
from bpy import context
from math import degrees
from math import radians
import re

ob = bpy.context.object

armature = context.scene.objects['Armature'].data

bpy.ops.object.mode_set(mode='EDIT')

for bone in armature.edit_bones:
    print(bone.name)
    if  re.search("^.*.001$", bone.name): 
        armature.edit_bones.remove(bone)
for bone in armature.edit_bones:
    print(bone.name)
    if  re.search("^.*.002$", bone.name): 
        armature.edit_bones.remove(bone)
for bone in armature.edit_bones:
    print(bone.name)
    if  re.search("^.*.003$", bone.name): 
        armature.edit_bones.remove(bone)
for bone in armature.edit_bones:
    print(bone.name)
    if  re.search("^.*.004$", bone.name): 
        armature.edit_bones.remove(bone)



#VERTEX CLEAN
import bpy
import bmesh

# get active mesh
obj = bpy.context.object
me = obj.data

# get bMesh representation
bm = bmesh.from_edit_mesh(me)

# set your vertex index value
v_index = 0 

# iterate through the vertex group 
for group in obj.vertex_groups:
    print(group.name)
    group.name= group.name.replace(".001", "")
for group in obj.vertex_groups:
    print(group.name)
    group.name= group.name.replace(".002", "")
for group in obj.vertex_groups:
    print(group.name)
    group.name= group.name.replace(".003", "")
for group in obj.vertex_groups:
    print(group.name)
    group.name= group.name.replace(".004", "")