import os
from maya import cmds
from vendor.Qt import QtWidgets, QtCore, QtGui
# from vendor.QtGui import QStandardItemModel, QStandardItem
# from vendor.QtGui import QColor, QFont

# class ClassName(object):
#     def __init__(self, *args):
#         super(ClassName, self).__init__(*args))
        

class StandardItem(QtGui.QStandardItem):
    def __init__(self, txt='',font_size=12, set_bold=False, color=QtGui.QColor(255,255,255), pm_node=False):
        super(StandardItem, self).__init__()
        
        fnt = QtGui.QFont("Open Sans", font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
        self.pm_node = pm_node


        #witcher_name witcher
        #witcher_name ciri