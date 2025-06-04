from __future__ import annotations

import dataclasses

from dynamicprompts.commands import Command
from dynamicprompts.enums import SamplingMethod

@dataclasses.dataclass(frozen=True)
class CommentCommand(Command):
    """CommentCommand is a literal expression that will not be included in final prompt, but it will taken into account when using ConditionalCommand
        Meaining, you can write comments to search upon using conditions. You can also write comments mid prompt that will be ignored when generating prompt
    """
    literal: str
    sampling_method: SamplingMethod = SamplingMethod.RANDOM
