from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from src.ui.mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Scaper")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
