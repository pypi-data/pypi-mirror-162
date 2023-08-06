import dataclasses
import io
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Export the given model as ONNX."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        input_size: int = 224

    @dataclasses.dataclass
    class Outputs:
        data: bytes = None

    class PredictionModel(torch.nn.Module):
        def __init__(self, model):
            super().__init__()
            self._model = model

        def forward(self, x):
            return self._model.prediction_step(x)

    def execute(self, inputs):
        model = Task.PredictionModel(inputs.model)
        x = torch.randn(1, 3, self.config.input_size, self.config.input_size)
        with io.BytesIO() as bytes_io:
            torch.onnx.export(model, x, bytes_io)
            return self.Outputs(bytes(bytes_io.getbuffer()))
