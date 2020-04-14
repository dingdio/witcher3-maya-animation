"""
Drag and drop for Maya 2018+
"""
import os
import sys


try:
    import maya.mel
    import maya.cmds
    isMaya = True
except ImportError:
    isMaya = False


def onMayaDroppedPythonFile(*args, **kwargs):
    """This function is only supported since Maya 2017 Update 3"""
    pass


def _onMayaDropped():
    """Dragging and dropping this file into the scene executes the file."""

    srcPath = os.path.join(os.path.dirname(__file__), 'src')
    iconPath = os.path.join(srcPath, 'witcher3', 'resource', 'icons', 'icon.png')

    srcPath = os.path.normpath(srcPath)
    iconPath = os.path.normpath(iconPath)

    if not os.path.exists(iconPath):
        raise IOError('Cannot find ' + iconPath)

    for path in sys.path:
        if os.path.exists(path + '/witcher3/__init__.py'):
            maya.cmds.warning('Witcher 3 Tools is already installed at ' + path)

    command = '''
# -----------------------------------
# Witcher 3 Tools
# https://github.com/dingdio/witcher3-maya-animation
# -----------------------------------

import os
import sys
    
if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')
    
if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')
    
import witcher3
reload(witcher3)
witcher3.w3tool.RedManager(dock=False)
'''.format(path=srcPath)

    shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)
    maya.cmds.shelfButton(
        command=command,
        annotation='Witcher 3 Tools',
        sourceType='Python',
        image=iconPath,
        image1=iconPath,
        parent=parent
    )

    # print("\n// Witcher 3 Tools has been added to current shelf.")


if isMaya:
    _onMayaDropped()
