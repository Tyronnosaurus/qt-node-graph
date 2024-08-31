from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import QFile

from node_scene import Scene
from node_node import Node
from node_edge import Edge, EDGE_TYPE_BEZIER
from node_graphics_view import QDMGraphicsView


class NodeEditorWidget(QWidget):
    """ Main window of the application """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.stylesheet_filename = 'qss/nodestyle.qss'
        self.loadStylesheet(self.stylesheet_filename)

        self.initUI()


    def initUI(self):
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Create graphics scene
        self.scene = Scene()
        self.addNodes()


        # Create graphics view to show the scene
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle("Node Editor")
        self.show()


    def addNodes(self):
        """ Adds some sample nodes """
        node1 = Node(self.scene, "My Awesome Node 1", inputs=[0,0,0], outputs=[1])
        node2 = Node(self.scene, "My Awesome Node 2", inputs=[3,3,3], outputs=[1])
        node3 = Node(self.scene, "My Awesome Node 3", inputs=[2,2,2], outputs=[1])
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -150)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=EDGE_TYPE_BEZIER)



    def loadStylesheet(self, filename):
        print('STYLE loading:', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
