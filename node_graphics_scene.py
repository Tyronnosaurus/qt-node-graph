from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import QLine

import math


class QDMGraphicsScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Settings
        self.gridSize = 20
        self.gridSquares = 5

        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.scene_width = 64000
        self.scene_height = 64000
        self.setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height) # Start view in canvas center

        self.setBackgroundBrush(self._color_background)


    # Create background grid
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Preparations
        left   = int(math.floor(rect.left()))
        right  = int(math.ceil(rect.right()))
        top    = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # Compute lines to be drawn
        lines_light = []
        lines_dark = []

        darkLinesOffset = self.gridSize * self.gridSquares

        for x in range(first_left, right, self.gridSize):   # Vertical lines
            if (x % darkLinesOffset == 0):  lines_dark.append(QLine(x, top, x, bottom))
            else:                           lines_light.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):   # Horizontal lines
            if (y % darkLinesOffset == 0):  lines_dark.append(QLine(left, y, right, y))
            else:                           lines_light.append(QLine(left, y, right, y))

        # Draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(lines_dark)

