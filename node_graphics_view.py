from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtCore import Qt, QEvent


class QDMGraphicsView(QGraphicsView):

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene
        
        self.initUI()
        
        self.setScene(self.grScene)

        self.zoomInFactor = 1.25
        self.zoom = 10  # Current zoom
        # self.zoomStep = 1
        # self.zoomClamp = False
        # self.zoomRange = [0, 10]



    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)    #Anchor for when zooming out and in



    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.MiddleButton):
            self.middleMouseButtonPressed(event)
        elif (event.button() == Qt.MouseButton.LeftButton):
            self.leftMouseButtonPress(event)
        elif (event.button() == Qt.MouseButton.RightButton):
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.MouseButton.MiddleButton):
            self.middleMouseButtonReleased(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    
    def middleMouseButtonPressed(self, event):
        # Just in case, release any previous mouse button events
        releaseEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)

        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # SetDragMode only works with the left mouse button, so we'll fake a buttonpress to be able to drag while still pressing the middle button
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)


    def middleMouseButtonReleased(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, event.buttons(), event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)



    def leftMouseButtonPress(self, event):
        return super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        return super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)


    def wheelEvent(self, event):
        # Calculate zoom Factor
        

        # Calculate zoom
        if event.angleDelta().y() > 0:  # Scroll wheel up (zoom in)
            zoomFactor = self.zoomInFactor
        else:                           # Scroll wheel down (zoom out)
            zoomFactor = 1 / self.zoomInFactor

        # Set scene scale (same for both axes)
        self.scale(zoomFactor, zoomFactor)
