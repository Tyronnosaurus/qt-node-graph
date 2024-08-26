from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPen, QPainterPath

import math
from node_socket import RIGHT_TOP, RIGHT_BOTTOM, LEFT_BOTTOM, LEFT_TOP


EDGE_CP_ROUNDNESS = 100



class QDMGraphicsEdge(QGraphicsPathItem):
    """ Graphical representation of an edge. This class should not be instantiated directly; use QDMGraphicsEdgeDirect or QDMGraphicsEdgeBezier """

    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge

        # Visual style (color, line type, line width) of the edges for when normal/slected/dragging
        self._color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(2.0)
        self._pen_selected.setWidthF(4.0)
        self._pen_dragging.setWidthF(4.0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setZValue(-1)

        self.posSource = [0, 0]
        self.posDestination = [200, 100]


    def setSource(self, x, y):
        """ Sets the coordinates of the start point """
        self.posSource = [x, y]

    def setDestination(self, x, y):
        """ Sets the coordinates of the end point """
        self.posDestination = [x, y]


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """ Overrides QGraphicsPathItem.paint(). Called whenever the edge is redrawn. """
        self.updatePath()

        if (self.edge.end_socket is None):  # If edge has no end socket, it means it's being dragged
            painter.setPen(self._pen_dragging)
        elif (self.isSelected()):
            painter.setPen(self._pen_selected)        
        else:
            painter.setPen(self._pen)

        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())


    def updatePath(self):
        """ Will handle drawing QPainterPath from Point A to B """
        raise NotImplemented("This method has to be overriden in a child class")




class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    """ To draw an edge with a straight line """
    def updatePath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        self.setPath(path)



class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    """ To draw an edge with a bezier curve """
    def updatePath(self):
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5
        
        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        sspos = self.edge.start_socket.position

        if (s[0]>d[0] and sspos in (RIGHT_TOP, RIGHT_BOTTOM)) or (s[0]<d[0] and sspos in (LEFT_BOTTOM, LEFT_TOP)):
            cpx_d *= -1
            cpx_s *= -1
            cpy_d = ( (s[1]-d[1]) / math.fabs((s[1]-d[1]) if ((s[1]-d[1]) != 0) else 0.00001) ) * EDGE_CP_ROUNDNESS
            cpy_s = ( (d[1]-s[1]) / math.fabs((d[1]-s[1]) if ((d[1]-s[1]) != 0) else 0.00001) ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))        
        path.cubicTo( s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDestination[0], self.posDestination[1])
        self.setPath(path)
