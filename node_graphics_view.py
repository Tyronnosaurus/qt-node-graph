from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtCore import Qt, QEvent

from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge, EDGE_TYPE_BEZIER


MODE_NOOP = 1
MODE_EDGE_DRAG = 2

EDGE_DRAG_START_THRESHOLD = 10

DEBUG = True


class QDMGraphicsView(QGraphicsView):
    """
    Represents the view of the visible portion of a scene.
    """

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene
        
        self.initUI()
        
        self.setScene(self.grScene)

        self.mode = MODE_NOOP

        self.zoom = 10  # Current zoom
        self.zoomInFactor = 1.25
        self.zoomRange = [0, 20]    # To limit how many times we can scroll up or down



    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)    # Anchor for when zooming in and out
        self.setDragMode(QGraphicsView.RubberBandDrag)  # Enables selection of multiple components with a box using left mouse button



    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.MiddleButton):  self.middleMouseButtonPressed(event)
        elif (event.button() == Qt.MouseButton.LeftButton):  self.leftMouseButtonPress(event)
        elif (event.button() == Qt.MouseButton.RightButton): self.rightMouseButtonPress(event)
        else:                                                super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.MouseButton.MiddleButton):  self.middleMouseButtonReleased(event)
        elif (event.button() == Qt.MouseButton.LeftButton):  self.leftMouseButtonRelease(event)
        elif (event.button() == Qt.MouseButton.RightButton): self.rightMouseButtonRelease(event)
        else:                                                super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        if (self.mode == MODE_EDGE_DRAG):
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.grEdge.update()

        super().mouseMoveEvent(event)

    
    def middleMouseButtonPressed(self, event):
        # Just in case, release any previous mouse button events
        releaseEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)

        # Enable Drag mode. In this mode, the user can drag the canvas with the left mouse button
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # SetDragMode only works with the left mouse button, so we'll fake a buttonpress to be able to drag while still pressing the middle button
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)


    def middleMouseButtonReleased(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, event.buttons(), event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)



    def leftMouseButtonPress(self, event):
        # Get item which we clicked on
        item = self.getItemAtClick(event)

        # We store the position of last LMB click
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # Logic
        if (type(item) is QDMGraphicsSocket):
            if (self.mode == MODE_NOOP):
                # If we click on a socket, start dragging an edge 
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return

        if (self.mode == MODE_EDGE_DRAG):
            # If we click on a socket while already dragging an edge, stop dragging
            res = self.edgeDragEnd(item)
            if res: return

        # If we didn't click a socket, pass the event upwards
        super().mousePressEvent(event)


    def leftMouseButtonRelease(self, event):
        # Get item which we release mouse button on
        item = self.getItemAtClick(event)

        # Logic
        if (self.mode == MODE_EDGE_DRAG):
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return

        super().mouseReleaseEvent(event)


    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)

        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print('RMB DEBUG:', item.edge, ' connecting sockets:',
                                            item.edge.start_socket, '<-->', item.edge.end_socket)
            if type(item) is QDMGraphicsSocket: print('RMB DEBUG:', item.socket, 'has edge:', item.socket.edge)

            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes: print('    ', node)
                print('  Edges:')
                for edge in self.grScene.scene.edges: print('    ', edge)


    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)



    def getItemAtClick(self, event):
        """ Return the object on which we've clicked/release mouse button """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj


    def edgeDragStart(self, item):
        if DEBUG: print('View::edgeDragStart ~ Start dragging edge')
        if DEBUG: print('View::edgeDragStart ~   assign Start Socket to:', item.socket)
        self.previousEdge = item.socket.edge
        self.last_start_socket = item.socket
        self.dragEdge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        if DEBUG: print('View::edgeDragStart ~   dragEdge:', self.dragEdge)


    def edgeDragEnd(self, item):
        """ Return True if skip the rest of the code """
        self.mode = MODE_NOOP

        if (type(item) is QDMGraphicsSocket):
            if DEBUG: print('View::edgeDragEnd ~   previous edge:', self.previousEdge)
            if item.socket.hasEdge():
                item.socket.edge.remove()
            if DEBUG: print('View::edgeDragEnd ~   assign End Socket', item.socket)
            if self.previousEdge is not None: self.previousEdge.remove()
            if DEBUG: print('View::edgeDragEnd ~  previous edge removed')
            self.dragEdge.start_socket = self.last_start_socket
            self.dragEdge.end_socket = item.socket
            self.dragEdge.start_socket.setConnectedEdge(self.dragEdge)
            self.dragEdge.end_socket.setConnectedEdge(self.dragEdge)
            if DEBUG: print('View::edgeDragEnd ~  reassigned start & end sockets to drag edge')
            self.dragEdge.updatePositions()
            return True

        if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
        self.dragEdge.remove()
        self.dragEdge = None
        if DEBUG: print('View::edgeDragEnd ~ about to set socket to previous edge:', self.previousEdge)
        if self.previousEdge is not None:
            self.previousEdge.start_socket.edge = self.previousEdge
        if DEBUG: print('View::edgeDragEnd ~ everything done.')
        return False


    def distanceBetweenClickAndReleaseIsOff(self, event):
        """ Measures if we are too far from the last LMB click scene position """
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        dist_sq = dist_scene.x()**2 + dist_scene.y()**2
        return dist_sq > EDGE_DRAG_START_THRESHOLD**2



    def wheelEvent(self, event):

        # Calculate zoom
        if event.angleDelta().y() > 0:  # Scroll wheel up (zoom in)
            zoomFactor = self.zoomInFactor
            self.zoom += 1
        else:                           # Scroll wheel down (zoom out)
            zoomFactor = 1 / self.zoomInFactor
            self.zoom -= 1

        # Check for zoom clamping
        clamped = False
        if (self.zoom < self.zoomRange[0]):
            self.zoom = self.zoomRange[0]
            clamped = True
        if (self.zoom > self.zoomRange[1]):
            self.zoom = self.zoomRange[1]
            clamped = True

        # Set scene scale (same for both axes)
        if (not clamped):
            self.scale(zoomFactor, zoomFactor)
