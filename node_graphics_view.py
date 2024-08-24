from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt


class QDMGraphicsView(QGraphicsView):

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene
        
        self.initUI()
        
        self.setScene(self.grScene)


    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)