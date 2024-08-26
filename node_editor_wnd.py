from PySide6.QtWidgets import QWidget, QVBoxLayout

from node_scene import Scene
from node_node import Node
from node_graphics_view import QDMGraphicsView


class NodeEditorWnd(QWidget):
    """ Main window of the application """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()


    def initUI(self):
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Create graphics scene
        self.scene = Scene()
        node = Node(self.scene, "My Awesome Node")

        # Create graphics view to show the scene
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle("Node Editor")
        self.show()
