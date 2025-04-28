# src/my_types.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class IgnoreType:
    value: str


@dataclass
class ResultType:
    post_url: str
    post_content: str
