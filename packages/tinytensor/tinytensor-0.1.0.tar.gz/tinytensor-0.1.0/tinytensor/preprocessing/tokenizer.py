import logging
import os
import numpy as np
try:
    from tokenizers import Tokenizer
except ImportError:
    logging.warning("Huggingface tokenizers not installed ")
from tinytensor.preprocessing.abstract import Preprocessing


class TextProcessing(Preprocessing):

    def __init__(self, configuration) -> None:
        self.tokenizer = Tokenizer.from_file(
            os.path.join(configuration['_dir'], configuration['tokenizer_file'])
        )
        self.name = configuration["name"]

    def __call__(self, inputs, model_inputs):
        text = inputs[self.name]
        if isinstance(text, str):
            text = [text]

        tokens = np.array([ encode.ids \
                for encode in self.tokenizer.encode_batch(text) ])
        model_inputs[self.name] = tokens
        return model_inputs


