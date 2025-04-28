from PyQt6.QtWidgets import QWidget

from src.ui.thread_container_ui import Ui_ThreadContainer


class ThreadContainer_Widget(QWidget, Ui_ThreadContainer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
