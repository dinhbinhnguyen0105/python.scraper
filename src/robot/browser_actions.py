import random, traceback, sys
from time import sleep
from PyQt6.QtCore import QObject, pyqtSignal
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from src import constants
from src.my_types import TaskInfo
from src.robot import selectors

MIN = 60_000


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
    page.goto("https://www.facebook.com/groups/feed/", timeout=MIN)
    # page_language = page.locator("html").get_attribute("lang")
    # if page_language != "en":
    #     signals.log_message.emit("Switch to English.")
    #     return
    sidebar_locator = page.locator(
        f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})"
    )
    while sidebar_locator.first.locator(selectors.S_LOADING).count():
        _ = sidebar_locator.first.locator(selectors.S_LOADING)
        if _.count():
            try:
                sleep(3)
                _.first.scroll_into_view_if_needed(timeout=100)
            except:
                break
    group_locators = sidebar_locator.first.locator(
        "a[href^='https://www.facebook.com/groups/']"
    )

    # TODO get group urls
    group_urls = []
    for group_locator in group_locators.all():
        group_text = group_locator.text_content()
        group_url = group_locator.get_attribute("href")
        is_in_targets = False
        is_not_in_ignores = False
        if task_info.target_keywords:
            _ = False
            for target_keyword in task_info.target_keywords:
                if target_keyword in group_text:
                    _ = True
                    break
            if _:
                is_in_targets = _
            else:
                continue
        else:
            is_in_targets = True

        if task_info.ignore_keywords:
            _ = True
            for ignore_keyword in task_info.ignore_keywords:
                if ignore_keyword in group_text:
                    _ = False
                    break
            if _:
                is_not_in_ignores = _
            else:
                continue
        else:
            is_not_in_ignores = True

        if is_in_targets and is_not_in_ignores:
            group_urls.append(group_url)
        else:
            continue

    # TODO crawl


def close_dialog(page: Page):
    try:
        dialog_locators = page.locator(selectors.S_DIALOG)
        for dialog_locator in dialog_locators.all():
            if dialog_locator.is_visible() and dialog_locator.is_enabled():
                close_button_locators = dialog_locator.locator(selectors.S_CLOSE_BUTTON)
                sleep(random.uniform(0.2, 1.5))
                close_button_locators.last.click(timeout=MIN)
                dialog_locator.wait_for(state="detached", timeout=MIN)
        return True
    except PlaywrightTimeoutError:
        return False


ACTION_MAP = {
    constants.LAUNCHING: on_launching,
    constants.SCRAPING: on_scraping,
}
