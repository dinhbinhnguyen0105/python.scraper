import random
import time
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot, Qt
from playwright.sync_api import sync_playwright
from undetected_playwright import Tarnished

from src.my_types import TaskInfo
from src.robot.browser_actions import ACTION_MAP
from src import constants


class WorkerSignals(QObject):
    main_progress_signal = pyqtSignal(str, int, int)
    sub_progress_signal = pyqtSignal(str, int, int)
    error_signal = pyqtSignal(TaskInfo, int, str)  # task_info, retry_num, err_msg
    finished_signal = pyqtSignal(TaskInfo, int)  # task_info, retry_num
    log_message = pyqtSignal(str)


class BrowserWorker(QRunnable):
    def __init__(self, task_info: TaskInfo, retry_num: int):
        super().__init__()
        self.task_info = task_info
        self.retry_num = retry_num
        self.signals = WorkerSignals()

        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        try:
            action_function = ACTION_MAP.get(self.task_info.action_name, None)
            if not action_function:
                return False
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=self.task_info.user_data_dir,
                    headless=self.task_info.headless,
                    args=["--disable-blink-features=AutomationControlled"],
                    ignore_default_args=["--enable-automation"],
                )

                Tarnished.apply_stealth(context)
                page = context.new_page()
                action_function(
                    page=page,
                    task_info=self.task_info,
                    signals=self.signals,
                )
                context.close()
        except Exception as e:
            print(e)
            self.signals.error_signal.emit(self.task_info, self.retry_num, str(e))
        finally:
            self.signals.finished_signal.emit(self.task_info, self.retry_num)
            return

    # @pyqtSlot()
    # def _test_run(self):
    #     # test
    #     total_group = random.randint(5, 10)
    #     total_post = random.randint(10, 20)
    #     try:
    #         for i in range(total_group):
    #             self.signals.main_progress_signal.emit(
    #                 self.task_info.object_name, total_group, i
    #             )
    #             for j in range(total_post):
    #                 time.sleep(random.uniform(0.01, 0.1))
    #                 self.signals.sub_progress_signal.emit(
    #                     self.task_info.object_name, total_post, j
    #                 )
    #                 # if random.uniform(0, 10) < 0.5:
    #                 #     raise ZeroDivisionError("ERROR: ZeroDivisionError")

    #         self.signals.finished_signal.emit(self.task_info, self.retry_num)
    #     except Exception as e:
    #         self.signals.error_signal.emit(self.task_info, self.retry_num, str(e))
