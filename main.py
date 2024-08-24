import sys
from PySide6.QtWidgets import QApplication
from node_editor_wnd import NodeEditorWnd

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = NodeEditorWnd()

    sys.exit(app.exec())