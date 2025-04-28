from PyQt6.QtWidgets import QWidget, QFileDialog

from src.ui.thread_container_ui import Ui_ThreadContainer


class ThreadContainer_Widget(QWidget, Ui_ThreadContainer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.selected_dir_path = ""
        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        self.thread_input.setDisabled(True)

    def setup_events(self):
        self.pushButton.clicked.connect(self.handle_open_directory)

    def handle_open_directory(self):
        directory_path = QFileDialog.getExistingDirectory(
            self,
            "Select user_data_dir",
            "",
            QFileDialog.Option.ShowDirsOnly,
        )
        if directory_path:
            self.thread_input.setText(directory_path)
            self.selected_dir_path = directory_path
