from __future__ import annotations

import ast

from .base import CheckerBase
from .data import Settings

COMMAND_ARGS = {"command"}
CONFIGURE_METHODS = {"config", "configure"}


class TK111(CheckerBase):
    message = "Calling '{handler}' instead of referencing it for 'command' argument. Perhaps you meant 'command={handler}' (without the parentheses)?"

    @staticmethod
    def detect(node: ast.Call) -> bool:
        if isinstance(node.func.value, ast.Name) and (
            node.func.value.id in {Settings.tkinter_as, Settings.ttk_as}
            or node.func.attr in CONFIGURE_METHODS
        ):
            for keyword in node.keywords:
                if keyword.arg in COMMAND_ARGS and isinstance(keyword.value, ast.Call):
                    return True

    @staticmethod
    def get_data(node: ast.Call) -> dict[str, str]:
        for keyword in node.keywords:
            if keyword.arg == "command":
                if isinstance(keyword.value.func, ast.Name):
                    return {"handler": keyword.value.func.id}
                elif isinstance(keyword.value.func, ast.Attribute):
                    return {
                        "handler": ".".join(
                            [keyword.value.func.value.id, keyword.value.func.attr]
                        )
                    }
                else:
                    raise NotImplementedError(
                        "Oh, crap! This is an error with flake8-tkinter.\n\
                     Please report this error here: https://github.com/rdbende/flake8-tkinter/issues/new"
                    )

    @staticmethod
    def get_pos(node: ast.Call) -> tuple[int, int]:
        for keyword in node.keywords:
            if keyword.arg in COMMAND_ARGS and isinstance(keyword.value, ast.Call):
                return keyword.value.lineno, keyword.value.col_offset
