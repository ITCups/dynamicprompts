from __future__ import annotations

import dataclasses
from typing import List

from dynamicprompts.commands import Command
from dynamicprompts.enums import SamplingMethod

@dataclasses.dataclass(frozen=True)
class Condition:
    # a key of a context to use to search for regex expression, if none then current context is used
    context_key: str | None
    regex_expression: str
    if_value: Command


@dataclasses.dataclass(frozen=True)
class ConditionCommand(Command):
    """Command that describes token used for including text based on condition, currently adds text if another text is already in a prompt"""
    # if_value will be inserted if regex_expression is true, else_value if false
    conditions_list: List[Condition]
    else_value: Command
    sampling_method: SamplingMethod = SamplingMethod.RANDOM