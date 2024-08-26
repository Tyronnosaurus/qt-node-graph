from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPen, QPainterPath


class QDMGraphicsEdge(QGraphicsPathItem):
    """ Graphical representation of an edge. This class should not be instantiated directly; use QDMGraphicsEdgeDirect or QDMGraphicsEdgeBezier """

    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge

        self._color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen.setWidthF(2.0)
        self._pen_selected.setWidthF(4.0)

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

        painter.setPen(self._pen if not self.isSelected() else self._pen_selected) # Use different pen if edge is selected
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
        if (s[0] > d[0]): dist *= -1

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0] + dist, s[1], d[0] - dist, d[1], self.posDestination[0], self.posDestination[1])
        self.setPath(path)
