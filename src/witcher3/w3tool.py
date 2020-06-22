import os

#local imports
import import_rig
reload(import_rig)
import entity
reload(entity)
import anims
reload(anims)
import cutscenes
reload(cutscenes)
import tree
reload(tree)
import material_utils
reload(material_utils)

#maya imports
import pymel.core as pm
from maya import cmds
from maya import OpenMayaUI as omui
from functools import partial

import logging
logging.basicConfig()
logger = logging.getLogger('RedManager')
logger.setLevel(logging.DEBUG)

##Qt imports
import vendor.Qt
from vendor.Qt import QtWidgets, QtCore, QtGui
if vendor.Qt.__binding__.startswith('PyQt'):
    logger.debug('Using sip')
    from sip import wrapinstance as wrapInstance
    from vendor.Qt.QtCore import pyqtSignal as Signal
elif vendor.Qt.__binding__ == 'PySide':
    logger.debug('Using shiboken')
    from shiboken import wrapInstance
    from vendor.Qt.QtCore import Signal
else:
    logger.debug('Using shiboken2')
    from shiboken2 import wrapInstance
    from vendor.Qt.QtCore import Signal

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

            parent = QtWidgets.QMainWindow(parent=getMayaMainWindow())
            parent.setObjectName('redManager')
            parent.setWindowTitle('Witcher 3 Tools')

            #dlgLayout = QtWidgets.QVBoxLayout(parent)

        super(RedManager, self).__init__(parent=parent)

        #self.buildUI()

        self.setupUi(parent)
        self.setup_buttons()
        self.parent().layout().addWidget(self)
        directory = os.path.join(pm.internalVar(userAppDir=True), 'witcher_rigs')
        #self.populate_cutscene(directory+"\\cutscenes\\cs104_keira_bath.w2cutscene.json")
        #self.populate_animSet(directory+"\\anims\\new_ciri.w2anims.json")
        #self.populate_animSet(directory+"\\anims\\ciri_mimic_animation.w2anims.json")
        self.populate_actors()

        if not dock:
            parent.show()

    def populate_actors(self):
        all = [p for p in pm.ls(type='transform') or [] if not pm.listRelatives(p, s=True)]
        for node in all:
            if node.hasAttr("witcher_name"):
                name = node.getAttr("witcher_name")
                item = self.actorListWidget.findItems(name, QtCore.Qt.MatchExactly)
                if len(item) <= 0:
                    __sortingEnabled = self.actorListWidget.isSortingEnabled()
                    self.actorListWidget.setSortingEnabled(False)
                    item = QtWidgets.QListWidgetItem()
                    self.actorListWidget.addItem(item)
                    item.setText(name)
                    self.actorListWidget.setSortingEnabled(__sortingEnabled)

    def getActorValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())
        for ix in self.actorListWidget.selectedIndexes():
            print(ix.data())

    def populate_animSet(self, fileName):
        animSetTemplate = anims.import_w3_animSet(fileName)
        self.loadedAnimSet = animSetTemplate
        #load animSet object
        #animSet object is just animation set
        #read all the animations???
        #populate the tree with that object
        

        #animsTreeView
        treeModel = QtGui.QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        animSet = tree.StandardItem("Animation Set", 10, set_bold=True);
        animSet.setEditable(False)
        animSet.setSelectable(False)
        animSet.setCheckable(False)

        for animSetEntry in animSetTemplate.animations:
            name = animSetEntry.animation.name
            animSet2 = tree.StandardItem(name, 10, pm_node=animSetEntry.animation);
            animSet.appendRow(animSet2)

        rootNode.appendRow(animSet)

        self.animsTreeView.setModel(treeModel)
        self.animsTreeView.expandAll()
        #self.animsTreeView.doubleClicked.connect(self.getValue)
        self.animsTreeView.clicked.connect(self.getValue)


    def populate_cutscene(self, fileName):
        cutsceneTemplate = cutscenes.import_w3_cutscene(fileName)
        self.loadedCutscene = cutsceneTemplate
        #load cutscene object
        #cutscene object is just animation set
        #read all the animations???
        #populate the tree with that object
        

        #cutsceneTreeView
        treeModel = QtGui.QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        cutscene = tree.StandardItem("Cutscene", 10, set_bold=True);
        cutscene.setEditable(False)
        cutscene.setSelectable(False)
        cutscene.setCheckable(False)

        for animSetEntry in cutsceneTemplate.animations:
            name = animSetEntry.animation.name
            cutscene2 = tree.StandardItem(name, 10, pm_node=animSetEntry);
            cutscene.appendRow(cutscene2)

        # all = [p for p in pm.ls(type='transform') or [] if not pm.listRelatives(p, s=True)]
        # for node in all:
        #     if node.hasAttr("witcher_name"):
        #         name = node.getAttr("witcher_name")
        #         cutscene2 = tree.StandardItem(name, 12, pm_node=node);
        #         cutscene.appendRow(cutscene2)

        # cutscene2 = tree.StandardItem("ciri:root", 12);
        # cutscene3 = tree.StandardItem("witcher:root", 12);
        # cutscene4 = tree.StandardItem("camera:root", 12);
        # cutscene5 = tree.StandardItem("ciri:mimic", 12);
        # cutscene6 = tree.StandardItem("witcher:mimic", 12);

        # cutscene.appendRow(cutscene2)
        # cutscene.appendRow(cutscene3)
        # cutscene.appendRow(cutscene4)
        # cutscene.appendRow(cutscene5)
        # cutscene.appendRow(cutscene6)

        rootNode.appendRow(cutscene)

        self.cutsceneTreeView.setModel(treeModel)
        self.cutsceneTreeView.expandAll()
        #self.cutsceneTreeView.doubleClicked.connect(self.getValue)
        self.cutsceneTreeView.clicked.connect(self.getValue)

    def getValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())

        #for ix in self.cutsceneTreeView.selectedIndexes():
            #text = ix.data(Qt.EditRole) # or ix.data()
            #print(ix.data())
        # all = [p for p in pm.ls(type='transform') or [] if not pm.listRelatives(p, s=True)]
        # for node in all:
        #     if node.hasAttr("witcher_name"):
        #         name = node.getAttr("witcher_name")
        #         if name == val.data():
        #             print(node)
        # item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        # brush = QtGui.QBrush(QtGui.QColor(156, 145, 167))
        # brush.setStyle(QtCore.Qt.NoBrush)
        # item_0.setBackground(0, brush)
        # item_1 = QtWidgets.QTreeWidgetItem(item_0)
        # item_1 = QtWidgets.QTreeWidgetItem(item_0)

    def setup_buttons(self):
        self.importRigBtn.clicked.connect(self.importRig)
        self.exportRigBtn.clicked.connect(self.exportRig)
        self.importAnimBtn.clicked.connect(self.importAnims)
        self.exportAnimBtn.clicked.connect(self.exportAnims)
        self.importFacBtn.clicked.connect(self.importFac)
        self.exportFacBtn.clicked.connect(self.exportFac)
        self.addNS.clicked.connect(self.addNSFun)
        self.remNS.clicked.connect(self.remNSFun)
        self.attachRigBtn.clicked.connect(self.attachRig)
        self.actionImport_w2ent.triggered.connect(self.actionImport_ent)
        self.actionImport_w2cutscene.triggered.connect(self.actionImport_w2cut)
        self.actionImport_w2anims_json.triggered.connect(self.actionImport_w2anims)

        
        self.animLoadSelectedBtn.clicked.connect(self.animLoadSelected)

        self.loadAnimBtn.clicked.connect(self.importAnimsTree)
        self.loadAllBtn.clicked.connect(self.importAnimsTree)
        self.actorListWidget.clicked.connect(self.getActorValue)

    def setupUi(self, redManager):
        redManager.setObjectName("redManager")
        redManager.resize(945, 734)
        self.centralwidget = QtWidgets.QWidget(redManager)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.actorListLabel = QtWidgets.QLabel(self.centralwidget)
        self.actorListLabel.setObjectName("actorListLabel")
        self.gridLayout.addWidget(self.actorListLabel, 0, 0, 1, 1)
        self.actorListWidget = QtWidgets.QListWidget(self.centralwidget)
        self.actorListWidget.setObjectName("actorListWidget")
        self.gridLayout.addWidget(self.actorListWidget, 1, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.MainTab = QtWidgets.QWidget()
        self.MainTab.setObjectName("MainTab")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.MainTab)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.groupRig = QtWidgets.QGroupBox(self.MainTab)
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
        self.gridLayout_6.addWidget(self.groupRig, 0, 0, 1, 1)
        self.groupAnims = QtWidgets.QGroupBox(self.MainTab)
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
        self.gridLayout_6.addWidget(self.groupAnims, 1, 0, 1, 1)
        self.groupFac = QtWidgets.QGroupBox(self.MainTab)
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
        self.gridLayout_6.addWidget(self.groupFac, 2, 0, 1, 1)
        self.groupCons = QtWidgets.QGroupBox(self.MainTab)
        self.groupCons.setObjectName("groupCons")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupCons)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nstLabel = QtWidgets.QLabel(self.groupCons)
        self.nstLabel.setObjectName("nstLabel")
        self.horizontalLayout_2.addWidget(self.nstLabel)
        self.model_ns_target = QtWidgets.QLineEdit(self.groupCons)
        self.model_ns_target.setObjectName("model_ns_target")
        self.horizontalLayout_2.addWidget(self.model_ns_target)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.nsLabel = QtWidgets.QLabel(self.groupCons)
        self.nsLabel.setObjectName("nsLabel")
        self.horizontalLayout_12.addWidget(self.nsLabel)
        self.model_ns = QtWidgets.QLineEdit(self.groupCons)
        self.model_ns.setObjectName("model_ns")
        self.horizontalLayout_12.addWidget(self.model_ns)
        self.verticalLayout_2.addLayout(self.horizontalLayout_12)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.addNS = QtWidgets.QPushButton(self.groupCons)
        self.addNS.setObjectName("addNS")
        self.verticalLayout_14.addWidget(self.addNS)
        self.remNS = QtWidgets.QPushButton(self.groupCons)
        self.remNS.setObjectName("remNS")
        self.verticalLayout_14.addWidget(self.remNS)
        self.attachRigBtn = QtWidgets.QPushButton(self.groupCons)
        self.attachRigBtn.setObjectName("attachRigBtn")
        self.verticalLayout_14.addWidget(self.attachRigBtn)
        self.gridLayout_2.addLayout(self.verticalLayout_14, 0, 1, 1, 1)
        self.gridLayout_6.addWidget(self.groupCons, 3, 0, 1, 1)
        self.tabWidget.addTab(self.MainTab, "")
        self.animSetTab = QtWidgets.QWidget()
        self.animSetTab.setObjectName("animSetTab")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.animSetTab)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.animsTreeView = QtWidgets.QTreeView(self.animSetTab)
        self.animsTreeView.setObjectName("animsTreeView")
        self.gridLayout_9.addWidget(self.animsTreeView, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.animLoadSelectedBtn = QtWidgets.QPushButton(self.animSetTab)
        self.animLoadSelectedBtn.setObjectName("animLoadSelectedBtn")
        self.horizontalLayout_3.addWidget(self.animLoadSelectedBtn)
        self.gridLayout_9.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.tabWidget.addTab(self.animSetTab, "")
        self.Cutscene = QtWidgets.QWidget()
        self.Cutscene.setObjectName("Cutscene")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.Cutscene)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.cutsceneTreeView = QtWidgets.QTreeView(self.Cutscene)
        self.cutsceneTreeView.setObjectName("cutsceneTreeView")
        self.gridLayout_7.addWidget(self.cutsceneTreeView, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.loadAnimBtn = QtWidgets.QPushButton(self.Cutscene)
        self.loadAnimBtn.setObjectName("loadAnimBtn")
        self.horizontalLayout.addWidget(self.loadAnimBtn)
        self.loadAllBtn = QtWidgets.QPushButton(self.Cutscene)
        self.loadAllBtn.setObjectName("loadAllBtn")
        self.horizontalLayout.addWidget(self.loadAllBtn)
        self.gridLayout_7.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.tabWidget.addTab(self.Cutscene, "")
        self.template = QtWidgets.QWidget()
        self.template.setObjectName("template")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.template)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.treeWidget = QtWidgets.QTreeWidget(self.template)
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        brush = QtGui.QBrush(QtGui.QColor(156, 145, 167))
        brush.setStyle(QtCore.Qt.NoBrush)
        item_0.setBackground(0, brush)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.gridLayout_8.addWidget(self.treeWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.template, "")
        self.SettingsTab = QtWidgets.QWidget()
        self.SettingsTab.setObjectName("SettingsTab")
        self.formLayout = QtWidgets.QFormLayout(self.SettingsTab)
        self.formLayout.setObjectName("formLayout")
        self.checkBox = QtWidgets.QCheckBox(self.SettingsTab)
        self.checkBox.setObjectName("checkBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkBox)
        self.tabWidget.addTab(self.SettingsTab, "")
        self.gridLayout.addWidget(self.tabWidget, 1, 1, 1, 1)
        redManager.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(redManager)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 945, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        redManager.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(redManager)
        self.statusbar.setObjectName("statusbar")
        redManager.setStatusBar(self.statusbar)
        self.actionImport_w2ent = QtWidgets.QAction(redManager)
        self.actionImport_w2ent.setObjectName("actionImport_w2ent")
        self.actionImport_w2cutscene = QtWidgets.QAction(redManager)
        self.actionImport_w2cutscene.setObjectName("actionImport_w2cutscene")
        self.actionAbout = QtWidgets.QAction(redManager)
        self.actionAbout.setObjectName("actionAbout")
        self.actionImport_w2anims_json = QtWidgets.QAction(redManager)
        self.actionImport_w2anims_json.setObjectName("actionImport_w2anims_json")
        self.menuFile.addAction(self.actionImport_w2ent)
        self.menuFile.addAction(self.actionImport_w2cutscene)
        self.menuFile.addAction(self.actionImport_w2anims_json)
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(redManager)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(redManager)

    def retranslateUi(self, redManager):
        _translate = QtCore.QCoreApplication.translate
        redManager.setWindowTitle(_translate("redManager", "Witcher 3 Tools"))
        self.actorListLabel.setText(_translate("redManager", "Actors"))
        self.groupRig.setTitle(_translate("redManager", "w2rig.json"))
        self.rigLabel.setText(_translate("redManager", "Target Rig:"))
        self.rig.setText(_translate("redManager", "NOT LOADED"))
        self.importRigBtn.setText(_translate("redManager", "Import"))
        self.exportRigBtn.setText(_translate("redManager", "Export"))
        self.groupAnims.setTitle(_translate("redManager", "w2anims.json"))
        self.aloadLabel.setText(_translate("redManager", "Loaded Animation:"))
        self.aLabel.setText(_translate("redManager", "Animation Name:"))
        self.importAnimBtn.setText(_translate("redManager", "Import"))
        self.exportAnimBtn.setText(_translate("redManager", "Export"))
        self.groupFac.setTitle(_translate("redManager", "w2fac.json"))
        self.facLabel.setText(_translate("redManager", "Face Rig:"))
        self.importFacBtn.setText(_translate("redManager", "Import"))
        self.exportFacBtn.setText(_translate("redManager", "Export"))
        self.groupCons.setTitle(_translate("redManager", "Skeleton Constrain Tools"))
        self.nstLabel.setText(_translate("redManager", "Target Namespace"))
        self.nsLabel.setText(_translate("redManager", "Source Namespace"))
        self.addNS.setText(_translate("redManager", "Add"))
        self.remNS.setText(_translate("redManager", "Remove"))
        self.attachRigBtn.setText(_translate("redManager", "Attach"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.MainTab), _translate("redManager", "Main"))
        self.animLoadSelectedBtn.setText(_translate("redManager", "Load Selected"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.animSetTab), _translate("redManager", "Animation Set"))
        self.loadAnimBtn.setText(_translate("redManager", "Load Selected"))
        self.loadAllBtn.setText(_translate("redManager", "Load All"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Cutscene), _translate("redManager", "Cutscene"))
        self.treeWidget.headerItem().setText(0, _translate("redManager", "Name"))
        self.treeWidget.headerItem().setText(1, _translate("redManager", "Value"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("redManager", "CCutsceneTemplate"))
        self.treeWidget.topLevelItem(0).child(0).setText(0, _translate("redManager", "fadeBefore"))
        self.treeWidget.topLevelItem(0).child(0).setText(1, _translate("redManager", "1"))
        self.treeWidget.topLevelItem(0).child(1).setText(0, _translate("redManager", "fadeAfter"))
        self.treeWidget.topLevelItem(0).child(1).setText(1, _translate("redManager", "3"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.template), _translate("redManager", "Template"))
        self.checkBox.setText(_translate("redManager", "Import Face Poses"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.SettingsTab), _translate("redManager", "Settings"))
        self.menuFile.setTitle(_translate("redManager", "File"))
        self.menuAbout.setTitle(_translate("redManager", "Help"))
        self.actionImport_w2ent.setText(_translate("redManager", "Import w2ent.json"))
        self.actionImport_w2cutscene.setText(_translate("redManager", "Import w2cutscene.json"))
        self.actionAbout.setText(_translate("redManager", "About"))
        self.actionImport_w2anims_json.setText(_translate("redManager", "Import w2anims.json"))

    def getDirectory(self):
        directory = os.path.join(pm.internalVar(userAppDir=True), 'witcher_rigs')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    def importRig(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select Rig", directory, "w2rig (*.w2rig.json);;w3dyng (*.w3dyng.json);;All files (*)")
        if not fileName[0]:
            pass
        else:
            root_bone = import_rig.import_w3_rig(fileName[0])
            self.rig.setText(fileName[0])
            cmds.group( n='group1', em=True )
            cmds.parent( root_bone, 'group1' )
            cmds.select('group1');
            cmds.xform( ro=(90,0,180), s=(100,100,100))
        # mat_names=[
        #     "PC0000_00_Bandage",
        #     "PC0000_00_BodyA",
        #     "PC0000_00_BodyB",
        #     "PC0000_00_Eye",
        #     "PC0000_00_Eyebrow",
        #     "PC0000_00_Eyelash",
        #     "PC0000_00_Hair",
        #     "PC0000_00_Head",
        #     "PC0000_00_Mouth",
        #     "PC0000_00_Pants",
        #     "PC0000_00_Shirt",
        #     "PC0000_00_Skin"
        # ]
        # mat_names=[
        #     "WE0000_00_Body",
        #     "WE0000_00_Materia"
        # ]
        #mat_path= "F:\\FF7_Remake\\End\\Content\\GameContents\\Character\\Player\\PC0000_00_Cloud_Standard\\Material\\"
        #mat_path= "F:\\FF7_Remake\\End\\Content\\GameContents\\Character\\Weapon\\WE0000_00_Cloud_BusterSword\\Material\\"

        # model_path= "F:\\FF7_Remake\\End2\\Content\\GameContents\\Character\\Enemy\\EB0021_00_Sephiroth_Standard\\"
        # mat_names=[
        # "EB0021_00_BodyA",
        # "EB0021_00_BodyB",
        # "EB0021_00_Eye",
        # "EB0021_00_Eyebrow",
        # "EB0021_00_Eyelash",
        # "EB0021_00_Hair",
        # "EB0021_00_HairCore",
        # "EB0021_00_Head",
        # "EB0021_00_Mouth",
        # "EB0021_00_Skin"
        # ]
        # for mat_name in mat_names:
        #     material_utils.import_material(mat_name+".mat", model_path)

    def exportRig(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"w2rig (*.w2rig.json);;w3dyng (*.w3dyng.json)")
        if not fileName[0]:
            pass
        else:
            # fileName.setFileMode(QtWidgets.QFileDialog.AnyFile)
            # fileName.setFilter("W3 Json file (*.json)")
            # fileName.getSaveFileName(self, "Save as")
            import_rig.export_w3_rig(fileName[0])

    def importAnims(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select w2Anims.json", directory,"Animation Set (*.w2Anims.json);;Cutscene (*.w2cutscene.json) ")
        if not fileName[0]:
            pass
        else:
            scene_actor = self.getSceneActor()
            pm.select( scene_actor+"*", r=True, hi=True )
            pm.cutKey( )
            animData = anims.import_w3_animation(fileName[0], scene_actor)
            #animData = import_rig.import_w3_animation(fileName[0], rig_filename, "face") #TODO CHECK FOR FACE ANIMATIONS
            self.animationLoaded.setText(fileName[0])
            self.animationName.setText(animData.name)

    def animLoadSelected(self, all=False):
        print("loading animation")
        scene_actor = self.getSceneActor()
        pm.select( scene_actor+"*", r=True, hi=True )
        pm.cutKey( )
        SetEntry = self.getSelectedAnim(self.animsTreeView, self.loadedAnimSet)
        anims.import_w3_animation2(SetEntry.animation, scene_actor, type = "animation")

    def importAnimsTree(self, all=False):
        print("loading animation")
        scene_actor = self.getSceneActor()
        SetEntry = self.getSelectedAnim(self.cutsceneTreeView, self.loadedCutscene)
        anims.import_w3_animation2(SetEntry.animation, scene_actor, type = "animation")

    def getSelectedAnim(self, view_tree, animset):
        currentAnim = False
        for ix in view_tree.selectedIndexes():
            for anim in animset.animations:
                if anim.animation.name == ix.data():
                    currentAnim = anim
        return currentAnim

    def getSceneActor(self):
        scene_actor = "ciri"
        for ix in self.actorListWidget.selectedIndexes():
            scene_actor = ix.data()
        return scene_actor
        # if scene_actor == "Cutscene":
        #     scene_actor = "ciri"

    def exportAnims(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w2anims.json)")
        if not fileName[0]:
            pass
        else:
            scene_actor = self.getSceneActor()
            anim_name = self.animationName.text()
            rig_filename = self.rig.text()
            anims.export_w3_animation(fileName[0], rig_filename, anim_name, scene_actor)

    def importFac(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select Pose", directory,"Face (*.w3fac.json)")
        if not fileName[0]:
            pass
        else:
            self.fac.setText(fileName[0])
            root_bone = import_rig.import_w3_face(fileName[0])
            self.fac.setText(fileName[0])
            #cmds.group( n='groupFace1', em=True )
            #cmds.parent( root_bone, 'groupFace1' )
            #cmds.select('groupFace1');
            #cmds.xform( ro=(90,0,90), s=(100,100,100))

    def exportFac(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', directory,"W3 Json (*.w3fac.json)")
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
        source =  self.model_ns.text() #"ciri:Root"#
        target = self.model_ns_target.text() #"ciri:c_rig" #
        import_rig.constrain_w3_rig(source, target, mo=False)
        cmds.confirmDialog( title='Witcher 3',message='The rig has been attached.' )

    def actionImport_ent(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select Entity", directory,"W3 entity (*.w2ent.json)")
        if not fileName[0]:
            pass
        else:
            root_bone = entity.import_ent(fileName[0], self.checkBox.isChecked())
            print(root_bone)
            # self.rig.setText(fileName[0])
            # cmds.group( n='group1', em=True )
            # cmds.parent( root_bone, 'group1' )
            # cmds.select('group1');
            # cmds.xform( ro=(90,0,180), s=(100,100,100))
        self.populate_actors()

    def actionImport_w2cut(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select w2Anims.json", directory,"Cutscene (*.w2cutscene.json)")
        if not fileName[0]:
            pass
        else:
            print("Importing cutscene")
            self.populate_cutscene(fileName[0])
            #scene_actor = self.getSceneActor()
            #animData = anims.import_w3_animation(fileName[0], scene_actor)
            #animData = import_rig.import_w3_animation(fileName[0], rig_filename, "face") #TODO CHECK FOR FACE ANIMATIONS
            #self.animationLoaded.setText(fileName[0])
            #self.animationName.setText(animData.name)

    def actionImport_w2anims(self):
        directory = self.getDirectory()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Select w2Anims.json", directory,"Animation Set (*.w2Anims.json)")
        if not fileName[0]:
            pass
        else:
            print("Importing Animation Set")
            self.populate_animSet(fileName[0])

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

def create_hair(g, material, textureFile, mat_name):
    hairNode = pm.shadingNode('ShaderfxShader', asShader=True, name=mat_name)
    pm.other.shaderfx(sfxnode=hairNode, loadGraph="\\ShaderFX\\witcher_3_hair.sfx")

    hairNode.outColor >> g.surfaceShader
    textureFile.fileTextureName >> hairNode.OpacityMap

def import_mesh():
    model = r'D:\\Witcher_uncooked_clean\\characters\\models\\geralt\\body\\model\\t_01_mg__body.w2mesh'
    
    
    wolven_kit = "F:\sourcetree\Wolven-kit\WolvenKit\bin\Release\WolvenKit.exe"
    blender_script = r'F:\\witcher3\\blender-2.76-windows64\\SCRIPTS\\convert_fbx_drop.bat'


def test():
    import_mesh()
    # select -cl  ;
    # select -r mesh ;
    # file -force -options "none=0;" -typ "APEX/PhysX" -pr -es "C:/dress_px.PxProj";
    #     system("start D:/apex.bat" );


    #create_hair()
    #allMesh = pm.ls(type='mesh')
    #for mesh in allMesh:
        # if "cu:" in mesh.nodeName() and "Orig" not in mesh.nodeName():
        #     print(mesh)
        #     #Get the shading group from the selected mesh
        #     sg = mesh.outputs(type='shadingEngine')
        #     #print(sg)

        #     for g in sg:
        #         #sgInfo = g.connections(mat=True)
        #         for material in g.surfaceShader.listConnections():
        #             print(material)
        #             mat_name = material.getName()
        #             pm.rename(mat_name, mat_name+"_OLD")
        #             fileNode = material.connections(type='file')
        #             if fileNode:
        #                 for file in fileNode:
        #                     textureFile = pm.getAttr(file.fileTextureName)
        #                     print 'This is the file', str(textureFile)
        #                     create_hair(g, material, file, mat_name)
        # if "he:" in mesh.nodeName() and "Orig" not in mesh.nodeName():
        #     print(mesh)
        #     #Get the shading group from the selected mesh
        #     sg = mesh.outputs(type='shadingEngine')
        #     #print(sg)

        #     for g in sg:
        #         #sgInfo = g.connections(mat=True)
        #         for material in g.surfaceShader.listConnections():
        #             #print(material)
        #             fileNode = material.connections(type='file')
        #             if fileNode:
        #                 for file in fileNode:
        #                     textureFile = pm.getAttr(file.fileTextureName)
        #                     if "eyelash" in textureFile:
        #                         mat_name = material.getName()
        #                         print("found eyelash on "+mat_name)
        #                         pm.rename(mat_name, mat_name+"_OLD")
        #                         create_hair(g, material, file, mat_name)
        #                         #print 'This is the file', str(textureFile)
        #             else:
        #                 if set(material.color.get()) == set([1.0, 1.0, 1.0]):
        #                     material.transparency.set([1.0, 1.0, 1.0, 1.0])
    #     sg = mesh.outputs(type='shadingEngine')
    #     for g in sg:
    #         for material in g.surfaceShader.listConnections():
    #             if material.diffuse:
    #                 material.diffuse.set(1.0)

                # sgInfo = g.connections(type='materialInfo')
                # if sgInfo:
                #     fileNode = sgInfo[0].connections(type='file')
                #     if fileNode:
                #         textureFile = pm.getAttr(fileNode[0].fileTextureName)
                #         print 'This is the file', str(textureFile)
                #     else:
                #         #sgInfo.color.set(0.700)
                #         print(sgInfo[0].getName())

    # mats = pm.ls(type='shader')
    # for f in mats:
    #     if "he:" in f.nodeName():
    #         #list = pm.listConnections(f)
    #         #print(list)
    #         print(f)
    # files = pm.ls(type='file')
    # for f in files:
    #     if "he:Diffuse" in f.nodeName():
    #         list = pm.listConnections(f)
    #         print(list)
    #         print(f)

    # material_name = "he:Material3"
    # tex_name = "he:DiffuseFBXASC032TextureFBXASC046001"

    #material_name = "cu:Material0"
    #tex_name = "cu:DiffuseFBXASC032Texture"

    # mat_m = pm.PyNode(material_name)
    # tex = pm.PyNode(tex_name)


    # remapColor = pm.shadingNode('remapColor', asUtility=True)
    # reverse = pm.shadingNode('reverse', asUtility=True)

    # remapColor.inputMin.set(0.700)
    # remapColor.outColor >> mat_m.transparency
    # remapColor.outColor >> reverse.input
    # reverse.output >> mat_m.specularColor
    # tex.outTransparency >> remapColor.color


    # object_methods = [method_name for method_name in dir(mat_m) if callable(getattr(mat_m, method_name))]
    # #cmds.setAttr ( (myBlinn + '.color'), Colors[0],Colors[1],Colors[2], type = 'double3' )  
    # cmds.setAttr ( (material_name + '.diffuse'), 1.0 ) 
