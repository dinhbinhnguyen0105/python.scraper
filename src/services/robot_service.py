# src/services/robot_service.py
import os
import json
from collections import deque
from typing import Any, List, Dict
from PyQt6.QtCore import QThreadPool, QObject, pyqtSignal, pyqtSlot

from src.my_types import TaskInfo
from src.robot.browser_worker import BrowserWorker


class RobotService(QObject):
    log_message = pyqtSignal(str)
    main_progress_signal = pyqtSignal(str, int, int)
    sub_progress_signal = pyqtSignal(str, int, int)
    finished_signal = pyqtSignal()
    data_signal = pyqtSignal(str, list)

    def __init__(self):
        super(RobotService, self).__init__()
        self.threadpool = QThreadPool.globalInstance()
        self.pending_tasks = deque()
        self.total_tasks_initial = 0
        self.retry_num = 0
        self.tasks_succeeded_num = 0
        self.tasks_failed_num = 0
        self.task_in_progress = {}

    def setup_threadpool(self, payload: Dict[str, Any]):
        max_thread = min(payload.get("thread_num", 1), self.threadpool.maxThreadCount())
        max_retries = payload.get("retry_num", 1)

        self.threadpool.setMaxThreadCount(max_thread)
        self.retry_num = max_retries

    @pyqtSlot(list)
    def add_tasks(self, task_list: List[TaskInfo]):
        for task in task_list:
            self.pending_tasks.append((task, self.retry_num))
        self.total_tasks_initial += len(task_list)
        self.log_message.emit(
            f"Add {len(task_list)} tasks; total={self.total_tasks_initial}"
        )
        self.try_start_tasks()

    @pyqtSlot()
    def try_start_tasks(self):
        while (
            self.pending_tasks
            and self.threadpool.activeThreadCount() < self.threadpool.maxThreadCount()
        ):
            task_info, retry_num = self.pending_tasks.popleft()
            worker = BrowserWorker(task_info=task_info, retry_num=retry_num)
            worker.signals.finished_signal.connect(self.on_worker_finished)
            worker.signals.error_signal.connect(self.on_worker_error)
            worker.signals.main_progress_signal.connect(self.on_worker_main_progress)
            worker.signals.sub_progress_signal.connect(self.on_worker_sub_progress)
            worker.signals.log_message.connect(self.on_worker_message)
            worker.signals.data_signal.connect(self.on_worker_data)
            self.task_in_progress[id(worker)] = (task_info, retry_num, worker)

            self.threadpool.start(worker)
            self.log_message.emit(
                f"Started task {task_info.dir_name} retry={retry_num}"
            )

    @pyqtSlot(TaskInfo, int)
    def on_worker_finished(self, task_info: TaskInfo, retry_num: int):
        worker_id = next(
            (
                key
                for key, value in self.task_in_progress.items()
                if value[0] is task_info
            ),
            None,
        )
        if worker_id is not None:
            del self.task_in_progress[worker_id]
        self.tasks_succeeded_num += 1
        self.log_message.emit(
            f"Task {task_info.dir_name} done. \
            {self.tasks_succeeded_num}/{self.total_tasks_initial}"
        )
        self.try_start_tasks()
        if self.tasks_succeeded_num + self.tasks_failed_num == self.total_tasks_initial:
            self.finished_signal.emit()

    @pyqtSlot(TaskInfo, int, str)
    def on_worker_error(self, task_info: TaskInfo, retry_num: int, message: str):
        self.log_message.emit(f"Error on {task_info.dir_name}: {message}")
        if retry_num > 0:
            self.pending_tasks.append((task_info, retry_num - 1))
            self.log_message.emit(
                f"Re-queue task {task_info.dir_name}, retries left {retry_num - 1}"
            )
        else:
            self.tasks_failed_num += 1
            self.log_message.emit(f"Task {task_info.dir_name} permanently failed.")
        self.try_start_tasks()

    @pyqtSlot(str, int, int)
    def on_worker_main_progress(
        self, object_name: str, total_group: int, current_group: int
    ):
        self.main_progress_signal.emit(object_name, total_group, current_group)

    @pyqtSlot(str, int, int)
    def on_worker_sub_progress(
        self, object_name: str, total_post: int, current_post: int
    ):
        self.sub_progress_signal.emit(object_name, total_post, current_post)

    @pyqtSlot(str)
    def on_worker_message(self, msg: str):
        self.log_message.emit(msg)

    @pyqtSlot(str, list)
    def on_worker_data(self, file_name: str, result: list):
        # self.data_signal.emit(result)
        os.makedirs("./results", exist_ok=True)  # Ensure the directory exists
        with open(
            os.path.join("./results", f"{file_name}.json"), mode="w", encoding="utf-8"
        ) as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        self.log_message.emit(f"Result saved to ./results/{file_name}.json")
