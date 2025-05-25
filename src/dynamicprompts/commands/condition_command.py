from __future__ import annotations

import dataclasses

from dynamicprompts.commands import Command
from dynamicprompts.enums import SamplingMethod



@dataclasses.dataclass(frozen=True)
class ConditionCommand(Command):
    """Command that describes token used for including text based on condition, currently adds text if another text is already in a prompt"""
    value: Command
    regex_expression: str = ""
    sampling_method: SamplingMethod = SamplingMethod.RANDOM
