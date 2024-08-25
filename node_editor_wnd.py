from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsItem, QPushButton, QTextEdit
from PySide6.QtGui import QBrush, QPen, QColor, QFont
from PySide6.QtCore import Qt

from node_scene import Scene
from node_graphics_view import QDMGraphicsView


class NodeEditorWnd(QWidget):

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
        self.grScene = self.scene.grScene


        # Create graphics view to show the scene
        self.view = QDMGraphicsView(self.grScene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle("Node Editor")
        self.show()

        self.addDebugContent()


    def addDebugContent(self):

        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.grScene.addText("This is my awesome text", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))

        widget1 = QPushButton("Hello World")
        proxy1 = self.grScene.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)

        widget2 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)

        line = self.grScene.addLine(-200, -100, 400, 200, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsSelectable)
        line.setFlag(QGraphicsItem.ItemIsMovable)