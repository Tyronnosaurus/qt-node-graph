from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPen, QPainter, QPolygonF, QPainterPath
from PySide6.QtCore import Qt, QPointF


class QDMCutLine(QGraphicsItem):
    """ Line that can be drawn hand-free while pressing LMB+Ctrl. Used to delete any edge that it crosses. """
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.line_points = []

        self._pen = QPen(Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3]) # Line is dashed

        self.setZValue(2) # Draw on top of edges and any other elements with Z=1 or less


    def boundingRect(self):         
        return self.shape().boundingRect()


    def shape(self):
        poly = QPolygonF(self.line_points)

        if (len(self.line_points) > 1):
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0,0))
            path.lineTo(QPointF(1,1))

        return path


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)

        painter.drawPolyline(poly)