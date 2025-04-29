# src/robot/browser_worker.py
import threading
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TargetClosedError
from undetected_playwright import Tarnished
from PyQt6.QtSql import QSqlDatabase

from src.my_types import TaskInfo
from src.robot.browser_actions import ACTION_MAP
from src import constants


class WorkerSignals(QObject):
    main_progress_signal = pyqtSignal(str, int, int)
    sub_progress_signal = pyqtSignal(str, int, int)
    error_signal = pyqtSignal(TaskInfo, int, str)  # task_info, retry_num, err_msg
    finished_signal = pyqtSignal(TaskInfo, int)  # task_info, retry_num
    log_message = pyqtSignal(str)
    data_signal = pyqtSignal(str, list)


class BrowserWorker(QRunnable):
    def __init__(self, task_info: TaskInfo, retry_num: int):
        super().__init__()
        self.task_info = task_info
        self.retry_num = retry_num
        self.signals = WorkerSignals()

        self.setAutoDelete(True)

    def _get_db(self) -> QSqlDatabase:
        """Tạo connection độc lập cho mỗi thread"""
        thread_id = threading.get_ident()
        conn_name = f"{constants.DB_CONNECTION}_{thread_id}"
        if not QSqlDatabase.contains(conn_name):
            # Cách 1: Tạo mới hoàn toàn
            db = QSqlDatabase.addDatabase("QSQLITE", conn_name)
            db.setDatabaseName(constants.DB_PATH)
            if not db.open():
                raise RuntimeError(
                    f"Cannot open DB in thread {thread_id}: {db.lastError().text()}"
                )
        return QSqlDatabase.database(conn_name)

    @pyqtSlot()
    def run(self):
        try:
            action_function = ACTION_MAP.get(self.task_info.action_name, None)
            if not action_function:
                return False
            db = self._get_db()
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
                # context.close()
        except TargetClosedError:
            return
        except Exception as e:
            print(e)
            self.signals.error_signal.emit(self.task_info, self.retry_num, str(e))
        finally:
            QSqlDatabase.removeDatabase(
                f"{constants.DB_CONNECTION}_{threading.get_ident()}"
            )
            self.signals.finished_signal.emit(self.task_info, self.retry_num)
            return
