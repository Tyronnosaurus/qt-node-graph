import os
import json

from PySide6.QtWidgets import QMainWindow, QLabel, QFileDialog, QApplication
from PySide6.QtGui import QAction
from node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    """
    Application wndow. Contains a menu bar with different actions, the actual node editor,
    and a status bar at the bottom
    """

    def __init__(self):
        super().__init__()

        self.initUI()

        self.filename = None # Holds name of the loaded file, for when we want to save it again


    def createAction(self, name, shortcut, tooltip, callback):
        """ Creates an action for the manu bar. An action is connected to a method and a shortcut """
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        return action


    def initUI(self):
        menubar = self.menuBar()

        # Create actions in the Menu bar
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.createAction('&New', 'Ctrl+N', "Create new graph", self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAction('&Open', 'Ctrl+O', "Open file", self.onFileOpen))
        fileMenu.addAction(self.createAction('&Save', 'Ctrl+S', "Save file", self.onFileSave))
        fileMenu.addAction(self.createAction('Save &As...', 'Ctrl+Shift+S', "Save file as...", self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAction('E&xit', 'Ctrl+Q', "Exit application", self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createAction('&Undo', 'Ctrl+Z', "Undo last operation", self.onEditUndo))
        editMenu.addAction(self.createAction('&Redo', 'Ctrl+Shift+Z', "Redo last operation", self.onEditRedo))
        editMenu.addSeparator()
        editMenu.addAction(self.createAction('Cu&t', 'Ctrl+X', "Cut to clipboard", self.onEditCut))
        editMenu.addAction(self.createAction('&Copy', 'Ctrl+C', "Copy to clipboard", self.onEditCopy))
        editMenu.addAction(self.createAction('&Paste', 'Ctrl+V', "Paste from clipboard", self.onEditPaste))
        editMenu.addSeparator()
        editMenu.addAction(self.createAction('&Delete', 'Del', "Delete selected items", self.onEditDelete))

        # Create node editor widget
        nodeeditor = NodeEditorWidget(self)
        self.setCentralWidget(nodeeditor)

        # Status bar
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)

        # Set window properties
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Node Editor")
        self.show()


    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText("Scene Pos: [%d, %d]" % (x, y))


    def onFileNew(self):
        self.centralWidget().scene.clear()


    def onFileOpen(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
        if (fname == ''): return
        if os.path.isfile(fname):
            self.centralWidget().scene.loadFromFile(fname)


    def onFileSave(self):
        """ Saves scene under the same filename it was opened from, without asking for confirmation """
        if (self.filename is None): return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage("Successfully saved %s" % self.filename)


    def onFileSaveAs(self):
        """ Opens dialog where user can select path and filename to save scene """
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')
        if (fname == ''): return
        self.filename = fname
        self.onFileSave()


    def onEditUndo(self):
        self.centralWidget().scene.history.undo()


    def onEditRedo(self):
        self.centralWidget().scene.history.redo()


    def onEditDelete(self):
        self.centralWidget().scene.grScene.views()[0].deleteSelected()

    
    def onEditCut(self):
        """ Serializes selected element, saves it on the application's clipboard, and deletes it from scene """
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        """ Serializes selected element and saves it on the application's clipboard """
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        raw_data = QApplication.instance().clipboard().text()

        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting of not valid json data!", e)
            return

        # Check if the json data are correct
        if ('nodes' not in data):
            print("JSON does not contain any nodes!")
            return

        self.centralWidget().scene.clipboard.deserializeFromClipboard(data)
