import random, traceback, sys
from time import sleep
from PyQt6.QtCore import QObject, pyqtSignal
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from src import constants
from src.my_types import TaskInfo


class WorkerSignals(QObject):
    main_progress_signal = pyqtSignal(str, int, int)
    sub_progress_signal = pyqtSignal(str, int, int)
    error_signal = pyqtSignal(TaskInfo, int, str)  # task_info, retry_num, err_msg
    finished_signal = pyqtSignal(TaskInfo, int)  # task_info, retry_num
    log_message = pyqtSignal(str)


def on_launching(
    page: Page,
    task_info: TaskInfo,
    signals: WorkerSignals,
):
    signals.log_message.emit(f"{task_info.dir_name} Launching ...")
    page.wait_for_event("close", timeout=0)
    signals.log_message.emit(f"{task_info.dir_name} Closed!")
    return True


def on_scraping(
    page: Page,
    task_info: TaskInfo,
    signals: WorkerSignals,
):

    pass


ACTION_MAP = {
    constants.LAUNCHING: on_launching,
    constants.SCRAPING: on_scraping,
}
