import sys
from PySide6.QtWidgets import QApplication
from node_editor_window import NodeEditorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = NodeEditorWindow()

    sys.exit(app.exec())