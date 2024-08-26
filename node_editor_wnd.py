from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import QFile

from node_scene import Scene
from node_node import Node
from node_graphics_view import QDMGraphicsView


class NodeEditorWnd(QWidget):
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
        node1 = Node(self.scene, "My Awesome Node 1", inputs=[1,2,3], outputs=[1])
        node2 = Node(self.scene, "My Awesome Node 2", inputs=[1,2,3], outputs=[1])
        node3 = Node(self.scene, "My Awesome Node 3", inputs=[1,2,3], outputs=[1])
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -150)


        # Create graphics view to show the scene
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle("Node Editor")
        self.show()


    def loadStylesheet(self, filename):
        print('STYLE loading:', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
