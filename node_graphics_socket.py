from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import QRectF


class QDMGraphicsSocket(QGraphicsItem):
    """ Graphical representation of a socket (the circle representing the inputs and outputs of a node) """
    
    def __init__(self, socket, socket_type=1):
        self.socket = socket
        super().__init__(socket.node.grNode)

        self.radius = 6.0
        self.outline_width = 1.0
        self._colors = [
            QColor("#FFFF7700"),
            QColor("#FF52e220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFb54747"),
            QColor("#FFdbe220"),
        ]
                
        self._color_background = self._colors[socket_type]

        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # Paint circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)


    def boundingRect(self):
        """ Reimplementation of QGraphicsItem.boundingRect(). Needed by Qt to know when to redraw the node. """
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
