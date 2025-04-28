from typing import List
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from src.ui.mainwindow_ui import Ui_MainWindow

from src.views.thread_container_w import ThreadContainer_Widget


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Scaper")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setup_ui()
        self.setup_events()

        self.thread_num = 0
        self.list_thread_widget: List[ThreadContainer_Widget] = []

    def setup_ui(self):
        self.thread_num_input.setValue(0)

    def setup_events(self):
        self.thread_num_input.valueChanged.connect(self.handle_change_thread)

    def handle_change_thread(self):
        current_thread_num = self.thread_num_input.value()
        spread = current_thread_num - self.thread_num
        if spread > 0:  # add thread
            while spread == 0:
                thread_container_widget = ThreadContainer_Widget(self)
                self.thread_container_layout.addWiget(thread_container_widget)
                # thread_container_widget.set
                self.list_thread_widget.append(thread_container_widget)
                spread -= 1
        elif spread < 0:  # remove thread
            while spread == 0:
                last_thread_widget = self.list_thread_widget.pop()
                last_thread_widget.deleteLater()
        else:
            pass

        self.list_thread_widget.append()

        self.thread_num = self.thread_num_input.value()
