from __future__ import annotations

import dataclasses

from dynamicprompts.commands import Command
from dynamicprompts.enums import SamplingMethod



@dataclasses.dataclass(frozen=True)
class ProbabilityCommand(Command):
    """Command that describes token used for including text based on probability"""
    value: Command
    # chance is capped at 1
    chance: float = 1.0
    # setting sampler as random because it uses other samples makes little sense when
    # we need pseudo random results
    sampling_method: SamplingMethod = SamplingMethod.RANDOM
