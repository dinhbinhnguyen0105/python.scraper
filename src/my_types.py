# src/my_types.py
from dataclasses import dataclass
from typing import List


@dataclass
class IgnoreType:
    value: str


@dataclass
class ResultType:
    post_url: str
    post_content: str


@dataclass
class TaskInfo:
    action_name: str
    object_name: str
    dir_name: str
    user_data_dir: str
    headless: str
    target_keywords: List[str]
    ignore_keywords: List[str]
    post_num: int
