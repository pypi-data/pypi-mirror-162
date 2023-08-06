from distutils.command.config import config
from .abstract import Postprocessing


class Regression(Postprocessing):
    def __init__(self, configuration) -> None:
        super().__init__()
        self.name = configuration['name']

    def __call__(self, outputs, chains):
        return outputs