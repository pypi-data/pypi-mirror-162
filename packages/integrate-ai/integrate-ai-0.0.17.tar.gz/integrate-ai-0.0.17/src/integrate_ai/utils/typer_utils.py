"""
Module containing miscellaneous typer utilities.
"""

from functools import wraps
from typing import Callable
import typer
import os


def toggle_prompt_wrapper(option_func: Callable, disable_prompts: str) -> Callable:
    """Decorates a function to remove prompt as a kwarg if disable_prompts is 'true'.

    Args:
        option_func (Callable): function to wrap.
        disable_promtps (str): whether to disable prompts or not ('true' if prompts should be disabled).

    Returns:
        decorated function (Callable): either same function as option_func or same function with prompt kwarg removed.
    """

    @wraps(option_func)
    def wrapper_func(*args, **kwargs):
        updated_kwargs = kwargs.copy()
        if disable_prompts == "true":
            updated_kwargs = kwargs.copy()
            updated_kwargs.pop("prompt")
            return option_func(*args, **updated_kwargs)
        else:
            return option_func(*args, **updated_kwargs)

    return wrapper_func


# wrapper around typer.Option to enable prompting to be condition on IAI_DISABLE_PROMPTS env variable
TogglePromptOption = toggle_prompt_wrapper(typer.Option, disable_prompts=os.environ.get("IAI_DISABLE_PROMPTS", ""))
