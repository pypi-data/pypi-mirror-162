import copy
import dataclasses
import io
import logging
import pathlib
import typing
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Load a state_dict from various sources.

    Supported sources are:
        1. a dictionary object. Use Inputs.state_dict.
        2. a bytes object. Use Inputs.state_dict_bytes.
        3. a file on local filesystem. Use Config.path.

    If config.strict is False, mismatched or missing parameters will be ignored.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module
        state_dict: typing.Optional[typing.Dict] = None
        state_dict_bytes: typing.Optional[bytes] = None

    @dataclasses.dataclass
    class Config:
        path: typing.Optional[pathlib.Path] = None
        strict: bool = True

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs: Inputs):
        num_sources = len([x for x in [inputs.state_dict, inputs.state_dict_bytes, self.config.path] if x])
        if num_sources != 1:
            raise ValueError("One state_dict source must be provided.")

        if inputs.state_dict:
            state_dict = inputs.state_dict
        if inputs.state_dict_bytes:
            state_dict = torch.load(io.BytesIO(inputs.state_dict_bytes), map_location='cpu')
        elif self.config.path:
            state_dict = torch.load(self._config.path, map_location='cpu')

        if not state_dict:
            raise ValueError("Failed to load the state_dict.")

        if not self.config.strict:
            # Filter parameters with different shape.
            existing_state_dict = inputs.model.state_dict()
            new_state_dict = {k: v for k, v in state_dict.items() if k in existing_state_dict and v.shape == existing_state_dict[k].shape}

            ignored_keys = set(state_dict) - set(new_state_dict)
            logger.info(f"Ignored {ignored_keys} since they have different shapes.")

            state_dict = new_state_dict

        model = copy.deepcopy(inputs.model)
        model.load_state_dict(state_dict, strict=self.config.strict)
        return self.Outputs(model)
