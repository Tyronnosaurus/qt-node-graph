from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPen, QPainter, QPolygonF
from PySide6.QtCore import Qt, QRectF


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
        return QRectF(0, 0, 1, 1)


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)