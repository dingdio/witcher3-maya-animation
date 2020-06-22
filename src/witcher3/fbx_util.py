import maya.cmds as cmds
import maya.mel as mel
import os

def importFbx(fbx_filename, ns="cake", name=":"):
    if not os.path.exists(fbx_filename):
        cmds.confirmDialog( title='Error', button='OK', message='Can\'t find "{0}". Check it exists.'.format( fbx_filename ))
    #set namespace
    ns = name+":"+ns
    currentNs = cmds.namespaceInfo(cur=True)
    cmds.namespace(relativeNames=True)
    if not cmds.namespace(ex=':%s'%ns):
        cmds.namespace(add=':%s'%ns)
    cmds.namespace(set=':%s'%ns)
    fbx_filename = fbx_filename.replace( '\\', '/' )


    #global tempVar
    #tempVar = fbx_filename
    #mel.eval( "$melVar = python(\"import witcher3.fbx_util;witcher3.fbx_util.tempVar\")" )
    #mel.eval( "print $melVar" )
    #mel.eval('FBXResetImport;')
    mel.eval('FBXProperty "Import|IncludeGrp|Geometry|OverrideNormalsLock" -v 1')
    #mel.eval('FBXProperty "Import|AdvOptGrp|Dxf|WeldVertices" -v 1')

    mel.eval('FBXImportMode -v Add')
    #mel.eval('FBXProperty "Import|IncludeGrp|MergeMode" -v Add')
    
    # mel.eval('FBXImportMergeAnimationLayers -v true')
    # mel.eval('FBXImportProtectDrivenKeys -v true')
    #mel.eval('FBXImportConvertDeformingNullsToJoint -v true')
    #mel.eval('FBXImportCacheFile -v false')
    
    # mel.eval('FBXImportMergeBackNullPivots -v false')
    # mel.eval('FBXImportSetLockedAttribute -v true')
    # mel.eval('FBXImportConstraints -v false')
 
    #mel.eval('file -f -new;')
    #mel.eval('file -import -type "FBX"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "{0}" "{1}";'.format( ns, fbx_filename ))
    mel.eval('FBXImport -f "{0}"'.format( fbx_filename ))
    #mel.eval('FBXResetImport;')
    
    #return current ns
    cmds.namespace(set=currentNs)
    cmds.namespace(relativeNames=False)
    return ns

##FBXProperties ##lists props

# class FBX_Exporter():
#     	def convert_to_joints( self ):
# 		pass

# 	def merge_mesh( self ):
# 		pass

# 	def export_mesh( self, file_path ):
# 		file_path = file_path.replace( '\\', '/' )
	
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups -v true;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|expHardEdges -v false;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|TangentsandBinormals -v true;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|SmoothMesh -v true;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|SelectionSet -v false;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|BlindData -v false;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|AnimationOnly -v false;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|GeometryNurbsSurfaceAs -v NURBS;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|Instances -v false;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|ContainerObjects -v true;" )
# 		mel.eval( "FBXProperty Export|IncludeGrp|Geometry|Triangulate -v false;" )

# 		mel.eval( "FBXExportInputConnections -v false;" )
# 		mel.eval( "FBXExportInAscii -v false;" )

# 		mel.eval( 'FBXExport -f "{0}" -s;'.format( file_path ) )
		
# 		maya_message.message( 'Export finished!' )

# 	def export_skin( self, file_path ):
# 		file_path = file_path.replace( '\\', '/' )

# 		mel.eval( "FBXExportAnimationOnly -v false;" )
# 		mel.eval( "FBXExportSkins -v true;" )
# 		mel.eval( "FBXExportScaleFactor 1.0" )

# 		mel.eval( "FBXExportInputConnections -v false;" )
# 		mel.eval( "FBXExportInAscii -v false;" )

# 		mel.eval( 'FBXExport -f "{0}" -s;'.format( file_path ) )
		
# 		maya_message.message( 'Export finished!' )

# 	def export_animation( self, file_path ):
# 		file_path = file_path.replace( '\\', '/' )
		
# 		start = str( cmds.playbackOptions( ast = True, q = True ) )
# 		end = str( cmds.playbackOptions( aet = True, q = True ) )

# 		mel.eval( "FBXExportBakeComplexAnimation -v true;" )

# 		mel.eval( 'FBXExportBakeComplexStart -v ' + start + ';' )
# 		mel.eval( 'FBXExportBakeComplexEnd -v ' + end + ';' )
			
# 		mel.eval( "FBXExportInputConnections -v false;" )
# 		mel.eval( "FBXExportInAscii -v false;" )

# 		mel.eval( 'FBXExport -f "{0}" -s;'.format( file_path ) )
		
# 		maya_message.message( 'Export finished!' )