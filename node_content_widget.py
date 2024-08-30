from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from collections import OrderedDict
from node_serializable import Serializable


class QDMNodeContentWidget(QWidget, Serializable):
    """ Widget that goes inside the node and contains elements such as labels, inputs... """
    
    def __init__(self, node, parent=None):
        super().__init__(parent)
        
        self.node = node

        self.initUI()


    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some Title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QDMTextEdit("foo"))

    def setEditingFlag(self, value):
        self.node.scene.grScene.views()[0].editingFlag = value


    def serialize(self):
        """ Returns the node content's properties as a dict for easy serialization """
        return OrderedDict([

        ])


    def deserialize(self, data, hashmap={}):
        return False



class QDMTextEdit(QTextEdit):
    """ Textbox that can be put inside a node's contents """
    
    def focusInEvent(self, event):
        """
        Raises a flag when we start editing text.
        Useful so that we can use the Del key to delete text without also deleting the whole node.
        """
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """ Lowers a flag when we stop editing text """
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
