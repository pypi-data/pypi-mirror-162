import onnxruntime as ort



class Model():

    def __init__(self, preprocess, postprocess, configuration) -> None:
        # handle code
        self.preprocess = preprocess
        self.ort = ort.InferenceSession(configuration['model'])
        self.postprocess = postprocess

    def forward(self, **kwargs):
        # pass to model
        # iterative decoding output
        return self.ort.run(None, kwargs)


    def predict(self, input):
        chain = {}
        for (name, preprocess) in self.preprocess:
            model_inputs = preprocess(input, chain)

        outputs = self.forward(**model_inputs)

        output_dict = {}
        for idx, (name, postprocess) in enumerate(self.postprocess):
            output_dict[name] = postprocess(outputs[idx], output_dict)
        return output_dict


