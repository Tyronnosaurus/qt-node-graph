from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit


class QDMNodeContentWidget(QWidget):
    """ Widget that goes inside the node and contains elements such as labels, inputs... """
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()


    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some Title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QTextEdit("foo"))
