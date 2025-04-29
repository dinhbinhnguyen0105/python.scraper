from typing import List
from PyQt6.QtWidgets import QMainWindow, QDialogButtonBox, QWidget
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from ui.mainwindow_ui import Ui_MainWindow

import constants
from controllers.robot_controller import RobotController
from views.thread_container_w import ThreadContainer_Widget


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Scraper")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.robot_controller = RobotController()

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
        self.group_key_input.setText("thuê, sang")
        self.ignore_group_key_input.setText("trọ")

    def setup_events(self):
        self.thread_num_input.valueChanged.connect(self.handle_change_thread)
        self.ok_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_btn.clicked.connect(self.handle_run)

    def handle_change_thread(self):
        current_thread_num = self.thread_num_input.value()
        spread = current_thread_num - self.thread_num
        if spread > 0:  # add thread
            while spread != 0:
                thread_container_widget = ThreadContainer_Widget(self)
                thread_container_widget.set_title(
                    f"Thread {len(self.list_thread_widget ) + 1}:"
                )
                thread_container_widget.launch_browser_btn.clicked.connect(
                    lambda: self.handle_launch_browser(thread_container_widget)
                )
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

    def handle_launch_browser(self, current_widget: ThreadContainer_Widget):
        user_data_dir_list = [current_widget.selected_dir_path]
        object_name_list = [current_widget.objectName()]
        target_group_keywords = [
            keyword.strip() for keyword in self.group_key_input.text().split(",")
        ]
        ignore_group_keywords = [
            keyword.strip() for keyword in self.ignore_group_key_input.text().split(",")
        ]
        self.robot_controller.run_task(
            action_name=constants.LAUNCHING,
            object_name_list=object_name_list,
            user_data_dir_list=user_data_dir_list,
            target_keywords=target_group_keywords,
            ignore_keywords=ignore_group_keywords,
        )

        current_widget.launch_browser_btn.setDisabled(True)
        self.robot_controller.log_message.connect(self.on_log_message)
        self.robot_controller.finished_signal.connect(
            lambda: current_widget.launch_browser_btn.setDisabled(False)
        )

    def handle_run(self):
        user_data_dir_list = [
            thread_widget.select_udd_input.text()
            for thread_widget in self.list_thread_widget
        ]
        object_name_list = [
            thread_widget.objectName() for thread_widget in self.list_thread_widget
        ]
        target_group_keywords = [
            keyword.strip()
            for keyword in self.group_key_input.text().split(",")
            if keyword.strip() != ""
        ]
        ignore_group_keywords = [
            keyword.strip()
            for keyword in self.ignore_group_key_input.text().split(",")
            if keyword.strip() != ""
        ]
        self.robot_controller.run_task(
            action_name=constants.SCRAPING,
            object_name_list=object_name_list,
            user_data_dir_list=user_data_dir_list,
            target_keywords=target_group_keywords,
            ignore_keywords=ignore_group_keywords,
        )

        self.ok_btn.setDisabled(True)

        self.robot_controller.finished_signal.connect(self.on_finished)
        self.robot_controller.main_progress_signal.connect(self.on_main_progress)
        self.robot_controller.sub_progress_signal.connect(self.on_sub_progress)
        self.robot_controller.log_message.connect(self.on_log_message)

    def on_finished(self):
        self.ok_btn.setDisabled(False)
        print("Finished")

    def on_main_progress(self, object_name: str, group_total: int, current_group: int):
        current_w: ThreadContainer_Widget = self.findChild(
            ThreadContainer_Widget,
            object_name,
        )
        main_progress = current_w.main_progress
        main_progress.setHidden(False)
        main_progress.setMinimum(0)
        main_progress.setMaximum(group_total)
        if main_progress.minimum() <= current_group <= main_progress.maximum():
            main_progress.setValue(current_group)
            current_w.main_progress_label.setHidden(False)
            current_w.main_progress_label.setText(f"{current_group}/{group_total}")

    def on_sub_progress(self, object_name: str, post_total: int, current_post: int):
        current_w: ThreadContainer_Widget = self.findChild(
            ThreadContainer_Widget,
            object_name,
        )
        sub_progress = current_w.sub_progress
        sub_progress.setHidden(False)
        sub_progress.setMinimum(0)
        sub_progress.setMaximum(post_total)
        if sub_progress.minimum() <= current_post <= sub_progress.maximum():
            sub_progress.setValue(current_post)
            current_w.sub_progress_label.setHidden(False)
            current_w.sub_progress_label.setText(f"{current_post}/{post_total}")

    def on_log_message(self, msg: str):
        print("Message: ", msg)
