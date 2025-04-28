# src/controllers/robot_controller.py
import os
from typing import List
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot
from src.my_types import TaskInfo
from src.services.robot_service import RobotService


class RobotController(QObject):
    finished_signal = pyqtSignal()
    main_progress_signal = pyqtSignal(str, int, int)
    sub_progress_signal = pyqtSignal(str, int, int)
    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.robot_service = RobotService()
        self.robot_service.main_progress_signal.connect(self.main_progress_signal)
        self.robot_service.sub_progress_signal.connect(self.sub_progress_signal)
        self.robot_service.log_message.connect(self.log_message)
        self.robot_service.finished_signal.connect(self.finished_signal)

    @pyqtSlot()
    def run_task(
        self,
        action_name: str,
        object_name_list: List[str],
        user_data_dir_list: List[str],
        target_keywords: List[str],
        ignore_keywords: List[str],
    ):
        settings_max_thread = len(user_data_dir_list)
        settings_max_retries = 3
        headless = False
        post_num = 200

        tasks = []
        for index, user_data_dir in enumerate(user_data_dir_list):
            if not os.path.exists(user_data_dir):
                continue
            task = TaskInfo(
                action_name=action_name,
                object_name=object_name_list[index],
                user_data_dir=user_data_dir,
                dir_name=os.path.basename(user_data_dir),
                headless=headless,
                target_keywords=target_keywords,
                ignore_keywords=ignore_keywords,
                post_num=post_num,
            )
            tasks.append(task)

        self.robot_service.setup_threadpool(
            {
                "thread_num": settings_max_thread,
                "retry_num": settings_max_retries,
            }
        )
        self.robot_service.add_tasks(task_list=tasks)
