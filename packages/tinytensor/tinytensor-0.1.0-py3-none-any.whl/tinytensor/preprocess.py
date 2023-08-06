import logging
from tinytensor.preprocessing.tokenizer import (
    TextProcessing
)

pipeline2class = {
    'text': TextProcessing
}


def make_preprocessing(main_configuration):

    processor = []
    for param_name, preprocess_config in main_configuration['inputs'].items():
        preprocess_config['_dir'] = main_configuration['dir']
        preprocess_config['name'] = param_name
        preprocess_type = preprocess_config['type']
        preprocess_cls = pipeline2class[preprocess_type]
        processor.append((param_name, preprocess_cls(preprocess_config)))
    return processor


