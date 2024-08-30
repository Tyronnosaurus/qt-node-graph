from PySide6.QtWidgets import QGraphicsView, QApplication
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtCore import Qt, QEvent

from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge, EDGE_TYPE_BEZIER
from node_graphics_cutline import QDMCutLine


MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3

EDGE_DRAG_START_THRESHOLD = 15

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
        self.editingFlag = False # Flag to indicate that we're editing text inside the node

        # Zoom
        self.zoom = 10  # Current zoom
        self.zoomInFactor = 1.25
        self.zoomRange = [0, 20]    # To limit how many times we can scroll up or down

        # Cutline
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)


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

        # If we're dragging the mouse (because we had already clicked LMB),
        # keep updating the edge's endpoint to wherever the mouse moves
        if (self.mode == MODE_EDGE_DRAG):
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.grEdge.update()
        
        # If we're currently making a cutline (with Ctrl+LMB), keep appending all the points the mouse moves through to a list
        # (since the line is irregular and can't be constructed from just a start and an end).
        if (self.mode == MODE_EDGE_CUT):
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.grScene.update()

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

        if DEBUG: print("LMB Click on", item, "MODS:", self.debug_modifiers(event))

        # By default, we can select multiple elements with LMB+Ctrl. We want to also be able to do it with LMB+Shift.
        # Here we detect LMB+Shift and mask it as if it were LMB+Ctrl.
        if (hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None):
            if (event.modifiers() & Qt.ShiftModifier):  # If pressed LMB + Shift
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        # If we click on a socket, start dragging an edge 
        if (type(item) is QDMGraphicsSocket):
            if (self.mode == MODE_NOOP):
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return

        # If we click on a socket while already dragging an edge, stop dragging
        if (self.mode == MODE_EDGE_DRAG):
            res = self.edgeDragEnd(item)
            if res: return

        if item is None:
            if (event.modifiers() & Qt.ControlModifier):
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return

        # After we've run our custom logic, pass the event upwards
        super().mousePressEvent(event)


    def leftMouseButtonRelease(self, event):
        # Get item which we release mouse button on
        item = self.getItemAtClick(event)

        # Just like above, when releasing LMB+Shift we fake an event to mask it as if it was LMB+Ctrl 
        if (hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None):
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        # If LMB released while dragging an edge
        if (self.mode == MODE_EDGE_DRAG):
            if self.distanceBetweenClickAndReleaseIsBigEnough(event): # Do nothing if LMB released very close to where it was pressed
                res = self.edgeDragEnd(item)    # Edge will snap to item if it is a socket
                if res: return

        #If LMB released while drawing a cutline
        if (self.mode == MODE_EDGE_CUT):
            self.cutIntersectingEdges()     # Delete the intersected edges
            self.cutline.line_points = []   # Forget all the points that make up the cutline
            self.grScene.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)  # Revert mouse cursor back to normal
            self.mode = MODE_NOOP
            return

        # After we've run our custom logic, pass the event upwards
        super().mouseReleaseEvent(event)


    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)

        if DEBUG:
            if isinstance(item, QDMGraphicsEdge):
                print('RMB DEBUG:', item.edge, ' connecting sockets:', item.edge.start_socket, '<-->', item.edge.end_socket)
            if type(item) is QDMGraphicsSocket:
                print('RMB DEBUG:', item.socket, 'has edge:', item.socket.edge)

            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes: print('    ', node)
                print('  Edges:')
                for edge in self.grScene.scene.edges: print('    ', edge)


    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)


    def keyPressEvent(self, event):
        """ Runs when a keyboard key is pressed. We can use it to do certain actions for different keys. """
        
        # If user presses Del key (and we're note editing text within the node), delete the node
        if (event.key() == Qt.Key_Delete):
            if not self.editingFlag:
                self.deleteSelected()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)


    def cutIntersectingEdges(self):
        """ Calculates intersections between cutline and edges, and deletes intersected edges """
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()


    def deleteSelected(self):
        """ Deletes all selected nodes and edges """
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()


    def debug_modifiers(self, event) -> str:
        """ Given an event, returns a string that says which modifier keys were being pressed """
        out = ""
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "
        return out


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
            if (item.socket != self.last_start_socket): # Do nothing if end socket is the same as start socket
                if DEBUG: print('View::edgeDragEnd ~   previous edge:', self.previousEdge)
                if item.socket.hasEdge(): item.socket.edge.remove()
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
        if (self.previousEdge is not None):
            self.previousEdge.start_socket.edge = self.previousEdge
        if DEBUG: print('View::edgeDragEnd ~ everything done.')
        return False


    def distanceBetweenClickAndReleaseIsBigEnough(self, event):
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
