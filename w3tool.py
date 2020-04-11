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

            #dlgLayout = QtWidgets.QVBoxLayout(parent)

        super(RedManager, self).__init__(parent=parent)

        #self.buildUI()
        self.setupUi(parent)
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

        importFacBtn = QtWidgets.QPushButton('Import w3fac.pose.json')
        importFacBtn.clicked.connect(self.importFac)
        layout.addWidget(importFacBtn, 2, 2)

        exportFacBtn = QtWidgets.QPushButton('Export w3fac.pose.json')
        exportFacBtn.clicked.connect(self.exportFac)
        layout.addWidget(exportFacBtn, 3, 2)

    def setupUi(self, redManager):
        redManager.setObjectName("redManager")
        redManager.resize(606, 641)
        self.gridLayout = QtWidgets.QGridLayout(redManager)
        self.gridLayout.setObjectName("gridLayout")
        self.groupRig = QtWidgets.QGroupBox(redManager)
        self.groupRig.setObjectName("groupRig")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupRig)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.rigLabel = QtWidgets.QLabel(self.groupRig)
        self.rigLabel.setObjectName("rigLabel")
        self.horizontalLayout_10.addWidget(self.rigLabel)
        self.rig = QtWidgets.QLineEdit(self.groupRig)
        self.rig.setObjectName("rig")
        self.horizontalLayout_10.addWidget(self.rig)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.importRigBtn = QtWidgets.QPushButton(self.groupRig)
        self.importRigBtn.setObjectName("importRigBtn")
        self.verticalLayout_6.addWidget(self.importRigBtn)
        self.exportRigBtn = QtWidgets.QPushButton(self.groupRig)
        self.exportRigBtn.setObjectName("exportRigBtn")
        self.verticalLayout_6.addWidget(self.exportRigBtn)
        self.horizontalLayout_10.addLayout(self.verticalLayout_6)
        self.verticalLayout_5.addLayout(self.horizontalLayout_10)
        self.gridLayout_5.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupRig, 1, 0, 1, 1)
        self.groupCons = QtWidgets.QGroupBox(redManager)
        self.groupCons.setObjectName("groupCons")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupCons)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.nsLabel = QtWidgets.QLabel(self.groupCons)
        self.nsLabel.setObjectName("nsLabel")
        self.horizontalLayout_12.addWidget(self.nsLabel)
        self.model_ns = QtWidgets.QLineEdit(self.groupCons)
        self.model_ns.setObjectName("model_ns")
        self.horizontalLayout_12.addWidget(self.model_ns)
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.addNS = QtWidgets.QPushButton(self.groupCons)
        self.addNS.setObjectName("addNS")
        self.verticalLayout_14.addWidget(self.addNS)
        self.remNS = QtWidgets.QPushButton(self.groupCons)
        self.remNS.setObjectName("remNS")
        self.verticalLayout_14.addWidget(self.remNS)
        self.horizontalLayout_12.addLayout(self.verticalLayout_14)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.attachRigBtn = QtWidgets.QPushButton(self.groupCons)
        self.attachRigBtn.setObjectName("attachRigBtn")
        self.verticalLayout_12.addWidget(self.attachRigBtn)
        self.horizontalLayout_12.addLayout(self.verticalLayout_12)
        self.gridLayout_2.addLayout(self.horizontalLayout_12, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupCons, 6, 0, 1, 1)
        self.groupFac = QtWidgets.QGroupBox(redManager)
        self.groupFac.setObjectName("groupFac")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupFac)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.facLabel = QtWidgets.QLabel(self.groupFac)
        self.facLabel.setObjectName("facLabel")
        self.horizontalLayout_11.addWidget(self.facLabel)
        self.fac = QtWidgets.QLineEdit(self.groupFac)
        self.fac.setObjectName("fac")
        self.horizontalLayout_11.addWidget(self.fac)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.importFacBtn = QtWidgets.QPushButton(self.groupFac)
        self.importFacBtn.setObjectName("importFacBtn")
        self.verticalLayout_9.addWidget(self.importFacBtn)
        self.exportFacBtn = QtWidgets.QPushButton(self.groupFac)
        self.exportFacBtn.setObjectName("exportFacBtn")
        self.verticalLayout_9.addWidget(self.exportFacBtn)
        self.horizontalLayout_11.addLayout(self.verticalLayout_9)
        self.verticalLayout_8.addLayout(self.horizontalLayout_11)
        self.gridLayout_4.addLayout(self.verticalLayout_8, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupFac, 4, 0, 1, 1)
        self.groupAnims = QtWidgets.QGroupBox(redManager)
        self.groupAnims.setObjectName("groupAnims")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupAnims)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.aloadLabel = QtWidgets.QLabel(self.groupAnims)
        self.aloadLabel.setObjectName("aloadLabel")
        self.horizontalLayout_13.addWidget(self.aloadLabel)
        self.animationLoaded = QtWidgets.QLineEdit(self.groupAnims)
        self.animationLoaded.setObjectName("animationLoaded")
        self.horizontalLayout_13.addWidget(self.animationLoaded)
        self.verticalLayout_16.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.aLabel = QtWidgets.QLabel(self.groupAnims)
        self.aLabel.setObjectName("aLabel")
        self.horizontalLayout_14.addWidget(self.aLabel)
        self.animationName = QtWidgets.QLineEdit(self.groupAnims)
        self.animationName.setObjectName("animationName")
        self.horizontalLayout_14.addWidget(self.animationName)
        self.verticalLayout_16.addLayout(self.horizontalLayout_14)
        self.gridLayout_3.addLayout(self.verticalLayout_16, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.importAnimBtn = QtWidgets.QPushButton(self.groupAnims)
        self.importAnimBtn.setObjectName("importAnimBtn")
        self.verticalLayout.addWidget(self.importAnimBtn)
        self.exportAnimBtn = QtWidgets.QPushButton(self.groupAnims)
        self.exportAnimBtn.setObjectName("exportAnimBtn")
        self.verticalLayout.addWidget(self.exportAnimBtn)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.groupAnims, 3, 0, 1, 1)

        self.retranslateUi(redManager)
        self.importRigBtn.clicked.connect(self.importRig)
        self.exportRigBtn.clicked.connect(self.exportRig)
        self.importAnimBtn.clicked.connect(self.importAnims)
        self.exportAnimBtn.clicked.connect(self.exportAnims)
        self.importFacBtn.clicked.connect(self.importFac)
        self.exportFacBtn.clicked.connect(self.exportFac)
        self.addNS.clicked.connect(self.addNSFun)
        self.remNS.clicked.connect(self.remNSFun)
        self.attachRigBtn.clicked.connect(self.attachRig)
        QtCore.QMetaObject.connectSlotsByName(redManager)
        redManager.setTabOrder(self.rig, self.importRigBtn)
        redManager.setTabOrder(self.importRigBtn, self.exportRigBtn)
        redManager.setTabOrder(self.exportRigBtn, self.animationLoaded)
        redManager.setTabOrder(self.animationLoaded, self.importAnimBtn)
        redManager.setTabOrder(self.importAnimBtn, self.animationName)
        redManager.setTabOrder(self.animationName, self.exportAnimBtn)
        redManager.setTabOrder(self.exportAnimBtn, self.fac)
        redManager.setTabOrder(self.fac, self.importFacBtn)
        redManager.setTabOrder(self.importFacBtn, self.exportFacBtn)
        redManager.setTabOrder(self.exportFacBtn, self.model_ns)
        redManager.setTabOrder(self.model_ns, self.addNS)
        redManager.setTabOrder(self.addNS, self.remNS)
        redManager.setTabOrder(self.remNS, self.attachRigBtn)

    def retranslateUi(self, redManager):
        _translate = QtCore.QCoreApplication.translate
        redManager.setWindowTitle(_translate("redManager", "Witcher 3 Tools"))
        self.groupRig.setTitle(_translate("redManager", "w2rig.json or w3fac.json"))
        self.rigLabel.setText(_translate("redManager", "Target Rig:"))
        self.rig.setText(_translate("redManager", "NOT LOADED"))
        self.importRigBtn.setText(_translate("redManager", "Import"))
        self.exportRigBtn.setText(_translate("redManager", "Export"))
        self.groupCons.setTitle(_translate("redManager", "Skeleton Constrain Tools"))
        self.nsLabel.setText(_translate("redManager", "Namespace:"))
        self.addNS.setText(_translate("redManager", "Add"))
        self.remNS.setText(_translate("redManager", "Remove"))
        self.attachRigBtn.setText(_translate("redManager", "Attach"))
        self.groupFac.setTitle(_translate("redManager", "w3fac.pose.json"))
        self.facLabel.setText(_translate("redManager", "Face Pose:"))
        self.importFacBtn.setText(_translate("redManager", "Import"))
        self.exportFacBtn.setText(_translate("redManager", "Export"))
        self.groupAnims.setTitle(_translate("redManager", "w2anims.json"))
        self.aloadLabel.setText(_translate("redManager", "Loaded Animation:"))
        self.aLabel.setText(_translate("redManager", "Animation Name:"))
        self.importAnimBtn.setText(_translate("redManager", "Import"))
        self.exportAnimBtn.setText(_translate("redManager", "Export"))


    def getDirectory(self):
        directory = os.path.join(pm.internalVar(userAppDir=True), 'witcher_rigs')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    def importRig(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select Rig", directory,"W3 Json (*.w2rig.json *.w3fac.json)")
        if not fileName[0]:
            pass
        else:
            root_bone = import_rig.import_w3_rig(fileName[0])
            self.rig.setText(fileName[0])
            cmds.group( n='group1', em=True )
            cmds.parent( root_bone, 'group1' )
            cmds.select('group1');
            cmds.xform( ro=(90,0,180), s=(100,100,100))

    def exportRig(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w2rig.json)")
        if not fileName[0]:
            pass
        else:
            # fileName.setFileMode(QtWidgets.QFileDialog.AnyFile)
            # fileName.setFilter("W3 Json file (*.json)")
            # fileName.getSaveFileName(self, "Save as")
            import_rig.export_w3_rig(fileName[0])

    def importAnims(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select w2Anims.json", directory,"W3 Json (*.w2Anims.json)")
        if not fileName[0]:
            pass
        else:
            rig_filename = self.rig.text()
            animData = import_rig.import_w3_animation(fileName[0], rig_filename)
            self.animationLoaded.setText(fileName[0])
            self.animationName.setText(animData.name)

    def exportAnims(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w2anims.json)")
        if not fileName[0]:
            pass
        else:
            anim_name = self.animationName.text()
            rig_filename = self.rig.text()
            import_rig.export_w3_animation(fileName[0], rig_filename, anim_name)

    def importFac(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select Pose", directory,"W3 Json (*.w3fac.pose.json)")
        if not fileName[0]:
            pass
        else:
            rig_filename = self.rig.text()
            animData = import_rig.import_w3_animation(fileName[0], rig_filename, "face")
            #import_rig.import_w3_rig(fileName[0])
            self.fac.setText(fileName[0])

    def exportFac(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w3fac.pose.json)")
        if not fileName[0]:
            pass
        else:
            pass
            #import_rig.export_w3_rig(fileName[0])

    def addNSFun(self):
        ns = self.model_ns.text()
        if not pm.namespace( exists=ns ):
            pm.namespace( add=ns )
        sel = pm.selected()
        for obj in sel:
            name = obj.swapNamespace(ns)
            obj.rename(name)
    def remNSFun(self):
        sel = pm.selected()
        for obj in sel:
            obj.rename(obj.stripNamespace())

    def attachRig(self):
        rig_filename = self.rig.text()
        ns = self.model_ns.text()
        import_rig.constrain_w3_rig(rig_filename, ns)

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
