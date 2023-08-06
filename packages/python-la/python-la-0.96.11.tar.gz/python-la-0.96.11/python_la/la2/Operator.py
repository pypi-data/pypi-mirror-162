from __future__ import annotations
from ..la1 import LinearMap, Field, Span
from typing import Callable


class Operator(LinearMap):
    def __init__(field: Field, func: Callable[[], ]) -> None:
        super().__init__(field, field, func)

    @property
    def isOrthogonoal(self) -> bool:
        pass
    # אורתוגונלי, אורתונורמלי. נורמלי. צמוד לעצמו

    def is_invariant_to(span: Span) -> bool:
        pass
