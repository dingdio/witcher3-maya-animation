import import_rig
reload(import_rig)
import json
import os
from maya import cmds
import Qt

import time
from Qt import QtWidgets, QtCore, QtGui

import logging

logging.basicConfig()
logger = logging.getLogger('RedManager')
logger.setLevel(logging.DEBUG)

if Qt.__binding__.startswith('PyQt'):
    logger.debug('Using sip')
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
elif Qt.__binding__ == 'PySide':
    logger.debug('Using shiboken')
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
else:
    logger.debug('Using shiboken2')
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

from maya import OpenMayaUI as omui

import pymel.core as pm

from functools import partial


class RedManager(QtWidgets.QWidget):
    def __init__(self, dock=False):
        if dock:
            parent = getDock()
        else:
            deleteDock()
            try:
                pm.deleteUI('redManager')
            except:
                logger.debug('No previous UI exists')

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName('redManager')
            parent.setWindowTitle('Witcher 3 Tools')

            dlgLayout = QtWidgets.QVBoxLayout(parent)

        super(RedManager, self).__init__(parent=parent)

        self.buildUI()
        self.parent().layout().addWidget(self)

        if not dock:
            parent.show()

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)
        directory = self.getDirectory()

        rigLabel = QtWidgets.QLabel()
        rigLabel.setText('Target Rig:')
        rig = QtWidgets.QLineEdit()
        rig.setText("NOT LOADED.")
        rig.setObjectName("Rig Name")
        layout.addWidget(rigLabel, 1, 0)
        layout.addWidget(rig, 1, 1, 1, 2)

        importRigBtn = QtWidgets.QPushButton('Import w2rig.json')
        importRigBtn.clicked.connect(self.importRig)
        layout.addWidget(importRigBtn, 2, 0)

        exportRigBtn = QtWidgets.QPushButton('Export w2rig.json')
        exportRigBtn.clicked.connect(self.exportRig)
        layout.addWidget(exportRigBtn, 3, 0)

        attachRigBtn = QtWidgets.QPushButton('Attach Rig')
        attachRigBtn.clicked.connect(self.attachRig)
        layout.addWidget(attachRigBtn, 4, 0)

        nsLabel = QtWidgets.QLabel()
        nsLabel.setText('Namespace:')
        layout.addWidget(nsLabel, 4, 1)
        model_ns = QtWidgets.QLineEdit()
        model_ns.setText("hiar_")
        layout.addWidget(model_ns, 4, 2)

        addNS = QtWidgets.QPushButton('Add NS')
        layout.addWidget(addNS, 5, 1)
        addNS.clicked.connect(self.addNS)
        remNS = QtWidgets.QPushButton('Remove NS')
        layout.addWidget(remNS, 5, 2)
        remNS.clicked.connect(self.remNS)

        aLabel = QtWidgets.QLabel()
        aLabel.setText('Animation Name:')
        layout.addWidget(aLabel, 7, 0)
        animationName = QtWidgets.QLineEdit()
        animationName.setText("default_name")
        layout.addWidget(animationName, 7, 1)

        importAnimBtn = QtWidgets.QPushButton('Import w2Anims.json')
        importAnimBtn.clicked.connect(self.importAnims)
        layout.addWidget(importAnimBtn, 2, 1)

        exportAnimBtn = QtWidgets.QPushButton('Export w2Anims.json')
        exportAnimBtn.clicked.connect(self.exportAnims)
        layout.addWidget(exportAnimBtn, 3, 1)

        importFacBtn = QtWidgets.QPushButton('Import w2fac.json')
        importFacBtn.clicked.connect(self.importFac)
        layout.addWidget(importFacBtn, 2, 2)

        exportFacBtn = QtWidgets.QPushButton('Export w2fac.json')
        exportFacBtn.clicked.connect(self.exportFac)
        layout.addWidget(exportFacBtn, 3, 2)

    def getDirectory(self):
        directory = os.path.join(pm.internalVar(userAppDir=True), 'witcher_rigs')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    def importRig(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select Rig", directory,"W3 Json (*.w2rig.json)")
        import_rig.import_w3_rig(fileName[0])

        rig = self.layout().itemAt(1).widget()
        rig.setText(fileName[0])
        cmds.group( n='group1', em=True )
        cmds.parent( 'Root', 'group1' )
        cmds.select('group1');
        cmds.xform( ro=(90,0,180), s=(100,100,100))

    def exportRig(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w2rig.json)")
        # fileName.setFileMode(QtWidgets.QFileDialog.AnyFile)
        # fileName.setFilter("W3 Json file (*.json)")
        # fileName.getSaveFileName(self, "Save as")
        import_rig.export_w3_rig(fileName[0])

    def attachRig(self):
        rig_filename = self.layout().itemAt(1).widget().text()
        ns = self.layout().itemAt(6).widget().text()
        import_rig.constrain_w3_rig(rig_filename, ns)

    def importAnims(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select w2Anims.json", directory,"W3 Json (*.w2Anims.json)")
        rig_filename = self.layout().itemAt(1).widget().text()
        import_rig.import_w3_animation(fileName[0], rig_filename)

    def exportAnims(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w2anims.json)")
        rig_filename = self.layout().itemAt(1).widget().text()
        import_rig.export_w3_animation(fileName[0], rig_filename)

    def importFac(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select w2Fac.json", directory,"W3 Json (*.w2Fac.json)")
        import_rig.import_w3_rig(fileName[0])

    def exportFac(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w2Fac.json)")
        import_rig.export_w3_rig(fileName[0])

    def addNS(self):
        ns = self.layout().itemAt(6).widget().text()
        if not pm.namespace( exists=ns ):
            pm.namespace( add=ns )
        sel = pm.selected()
        for obj in sel:
            name = obj.swapNamespace(ns)
            obj.rename(name)
    def remNS(self):
        sel = pm.selected()
        for obj in sel:
            obj.rename(obj.stripNamespace())


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


def getDock(name='RedManagerDock'):

    deleteDock(name)
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Witcher 3 Tools")
    qtCtrl = omui.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(long(qtCtrl), QtWidgets.QWidget)
    return ptr


def deleteDock(name='RedManagerDock'):
    if pm.workspaceControl(name, query=True, exists=True):
        pm.deleteUI(name)
