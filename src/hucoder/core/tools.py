from typing import NotRequired, TypedDict


class EditFileParam(TypedDict):
    path: str
    content: str
    start_line: NotRequired[int]
    end: NotRequired[int]
