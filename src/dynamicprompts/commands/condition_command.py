from __future__ import annotations

import dataclasses

from dynamicprompts.commands import Command
from dynamicprompts.enums import SamplingMethod



@dataclasses.dataclass(frozen=True)
class ConditionCommand(Command):
    """Command that describes token used for including text based on condition, currently adds text if another text is already in a prompt"""
    # if_value will be inserted if regex_expression is true, else_value if false
    if_value: Command
    else_value: Command
    regex_expression: Command
    sampling_method: SamplingMethod = SamplingMethod.RANDOM