import random, traceback, sys
from time import sleep
from PyQt6.QtCore import QObject, pyqtSignal
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator

from src import constants
from src.my_types import TaskInfo
from src.robot import selectors
from src.services.db_service import IgnorePhoneService, IgnoreUIDService, ResultService

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
    from src.database.database import initialize_database

    if not initialize_database():
        raise Exception("failed to initialize_database")

    page.goto("https://www.facebook.com/groups/feed/", timeout=MIN)
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
                if target_keyword.lower() in group_text.lower():
                    _ = True
                    break
            is_in_targets = _
        else:
            is_in_targets = True

        if task_info.ignore_keywords:
            _ = True
            for ignore_keyword in task_info.ignore_keywords:
                if ignore_keyword.lower() in group_text.lower():
                    _ = False
                    break
            is_not_in_ignores = _
        else:
            is_not_in_ignores = True
        if is_in_targets and is_not_in_ignores:
            group_urls.append(group_url)
        else:
            continue
    # TODO crawl
    for index, group_url in enumerate(group_urls):
        page.goto(group_url, timeout=MIN / 2)
        signals.main_progress_signal.emit(task_info.object_name, len(group_urls), index)
        close_dialog(page)
        feed_locators = page.locator(selectors.S_FEED)
        try:
            feed_locators.first.wait_for(state="attached", timeout=MIN / 2)
        except PlaywrightTimeoutError:
            continue
        feed_locator: Locator = feed_locators.first
        if not feed_locator:
            continue

        # task_info.post_num
        try:
            post_index = 0
            while True:
                article_locators = feed_locator.locator(selectors.S_ARTICLE)
                article_locators.first.scroll_into_view_if_needed()
                # nearest_parent = article_locators.first.locator(
                #     f"xpath=ancestor::div[count(.//div[@aria-describedby][@aria-labelledby]) > 2][1]"
                # ).first

                describedby_values = article_locators.first.get_attribute(
                    "aria-describedby"
                )
                article_user_id = article_locators.first.get_attribute(
                    "aria-labelledby"
                )
                (
                    article_info_id,
                    article_message_id,
                    article_content_id,
                    article_reaction_id,
                    article_comment_id,
                ) = describedby_values.split(" ")

                popup_locators = article_locators.first.locator(
                    "[aria-haspopup='menu'][aria-expanded='false']"
                )

                article_user_locator = article_locators.first.locator(
                    f"[id='{article_user_id}']"
                )
                article_info_locator = article_locators.first.locator(
                    f"[id='{article_info_id}']"
                )
                article_message_locator = article_locators.first.locator(
                    f"[id='{article_message_id}']"
                )
                article_content_locator = article_locators.first.locator(
                    f"[id='{article_content_id}']"
                )
                article_reaction_locator = article_locators.first.locator(
                    f"[id='{article_reaction_id}']"
                )
                article_comment_locator = article_locators.first.locator(
                    f"[id='{article_comment_id}']"
                )
                user_url = None
                info_url = None
                message = None
                content = None
                reaction = None
                comment = None
                try:
                    try:
                        article_user_locator.first.wait_for(
                            state="attached", timeout=1_000
                        )
                        article_user_locator.scroll_into_view_if_needed()
                        article_user_locator.highlight()
                        article_user_url_locator = article_user_locator.first.locator(
                            "a"
                        )
                        article_user_url_locator.first.hover()
                        sleep(0.5)
                        user_url = article_user_url_locator.first.get_attribute(
                            "href"
                        ).split("?")[0]
                        user_url = (
                            user_url[0:-1] if user_url.endswith("/") else user_url
                        )
                        print("user_url: ", user_url)
                        # TODO request data
                        popup_locators.first.hover()
                        sleep(0.5)
                        uid = user_url.split("/")[-1]
                        if IgnoreUIDService.is_field_value_exists(uid):
                            print("Passed")
                            continue
                        else:
                            print("Adding uid")
                            IgnorePhoneService.create({"value": uid})

                    except PlaywrightTimeoutError:
                        pass

                    try:
                        article_info_locator.first.wait_for(
                            state="attached", timeout=1_000
                        )
                        article_info_locator.scroll_into_view_if_needed()
                        article_info_locator.highlight()
                        article_info_url_locator = article_info_locator.first.locator(
                            "a"
                        )
                        article_info_url_locator.first.hover()
                        sleep(0.5)
                        info_url = article_info_url_locator.first.get_attribute(
                            "href"
                        ).split("?")[0]
                        info_url = (
                            info_url[0:-1] if info_url.endswith("/") else info_url
                        )
                        if not info_url:
                            continue
                        else:
                            print("info_url: ", info_url)
                            popup_locators.first.hover()
                            sleep(0.5)
                    except PlaywrightTimeoutError:
                        pass

                    try:
                        article_message_locator.first.wait_for(
                            state="attached", timeout=1_000
                        )
                        article_message_locator.scroll_into_view_if_needed()
                        article_message_locator.highlight()
                        try:
                            seemore_btn_locator = article_message_locator.first.locator(
                                selectors.S_BUTTON
                            )
                            seemore_btn_locator.click(timeout=500)
                        except PlaywrightTimeoutError:
                            pass
                        message = article_message_locator.first.text_content()

                    except PlaywrightTimeoutError:
                        pass

                    print()
                    signals.sub_progress_signal.emit(
                        task_info.object_name, task_info.post_num, post_index
                    )
                    post_index += 1
                    if post_index > task_info.post_num:
                        return

                except Exception as e:
                    print(e)
                    traceback.print_exc()
                article_locators.first.evaluate("elm => elm.remove()")
                # page.wait_for_event("close", timeout=0)

        except Exception as e:
            # print("ERROR in 'on_scraping': ", e)
            traceback.print_exc()


# 61571895352174


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


def find_nearest_ancestor(element: Locator, selector):
    current_element = element
    while current_element:
        elm = current_element.locator(selector).first

    return None


ACTION_MAP = {
    constants.LAUNCHING: on_launching,
    constants.SCRAPING: on_scraping,
}
