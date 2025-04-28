from typing import List
from PyQt6.QtWidgets import QMainWindow, QDialogButtonBox
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
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

        regex = QRegularExpression("^[a-zA-Z0-9 &,]+$")
        validator = QRegularExpressionValidator(regex)
        self.group_key_input.setValidator(validator)
        self.ignore_group_key_input.setValidator(validator)

        self.ok_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_btn.clicked.connect(self.handle_run)

    def setup_events(self):
        self.thread_num_input.valueChanged.connect(self.handle_change_thread)

    def handle_change_thread(self):
        current_thread_num = self.thread_num_input.value()
        spread = current_thread_num - self.thread_num
        if spread > 0:  # add thread
            while spread != 0:
                thread_container_widget = ThreadContainer_Widget(self)
                self.threads_container_layout.addWidget(thread_container_widget)
                self.list_thread_widget.append(thread_container_widget)
                spread -= 1
        elif spread < 0:  # remove thread
            while spread != 0:
                last_thread_widget = self.list_thread_widget.pop()
                self.threads_container_layout.removeWidget(last_thread_widget)
                last_thread_widget.deleteLater()
                spread += 1
        else:
            pass
        self.thread_num = current_thread_num

    def handle_run(self):
        list_udd = [
            thread_container_widget.selected_dir_path
            for thread_container_widget in self.list_thread_widget
        ]
        target_group_keywords = [
            keyword.strip() for keyword in self.group_key_input.text().split(",")
        ]
        ignore_group_keywords = [
            keyword.strip() for keyword in self.ignore_group_key_input.text().split(",")
        ]

        print(list_udd)
        print(target_group_keywords)
        print(ignore_group_keywords)

        # TODO start robot controller
