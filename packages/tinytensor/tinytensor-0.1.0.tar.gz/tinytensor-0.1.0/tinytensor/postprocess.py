import logging
from tinytensor.postprocessing.classification import (
    HierarchicalMultiClassification,
    Classification,
    TopkClassification
)
from tinytensor.postprocessing.regression import (
    Regression
)

pipeline2class = {
    'topk_classification': TopkClassification,
    'classification': Classification,
    'regression': Regression,
    'multi_hierarchical_classification': HierarchicalMultiClassification
}

def make_postprocessing(main_configuration):
    processor = []
    
    pipeline = [ (int(idx), preprocess_config) for idx, preprocess_config in main_configuration['outputs'].items()]
    pipeline = sorted(pipeline)
    for (order_id, config) in pipeline:
        type_ = config['output']
        config['_dir'] = main_configuration['dir']
        postprocess_cls = pipeline2class[type_]
        processor.append(
            ( config['name'], postprocess_cls(config))
        )
    return processor


