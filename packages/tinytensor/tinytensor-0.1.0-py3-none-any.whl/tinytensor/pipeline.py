import os
import json
from tinytensor.preprocess import make_preprocessing
from tinytensor.postprocess import make_postprocessing
from tinytensor.models import Model

def make_pipeline(config_path):
    config_filename = os.path.join(config_path, 'configuration.json')
    if not os.path.exists(config_filename):
        raise ValueError("configuration.json not found in {}".format(config_path))

    with open(config_filename, 'r') as f:
        config = json.load(f)
    config['dir'] = config_path
    preprocesses = make_preprocessing(config)
    postprocesses = make_postprocessing(config)
    config['model'] = os.path.join(config['dir'], config['model_file'])
    model = Model(
            preprocess=preprocesses,
            postprocess=postprocesses,
            configuration=config
        )

    return model


