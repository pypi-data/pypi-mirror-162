import sys
from habana_frameworks.mediapipe.operators.media_schema import schema as s
from habana_frameworks.mediapipe.operators.media_params import output_params
from habana_frameworks.mediapipe.backend import utils as mu


def operator_add(name):
    """
    Method to  add operator to fn.
    """
    class operator():
        """
        Class defining media operator.
        """

        def __init__(self, **kwargs):
            """
            Constructor method.

            """
            self.opname = str(type(self).__name__)
            self.device = None
            # layout is not mapped to any thing in c++ need to see how to handle it
            self.layout = ''
            self.output_scale = 1.0
            self.output_zerop = 0.0
            self.schema = s.get_operator_schema(type(self).__name__)
            self.out_info = output_params.copy()
            self.dtype = self.schema.getDtype()
            self.num_outputs = self.schema.getNumOutputs()
            if ("device" in kwargs.keys()):
                self.device = kwargs["device"]
                del kwargs["device"]
            if("output_scale" in kwargs.keys()):
                self.out_info["outputScale"] = kwargs["output_scale"]
                del kwargs["output_scale"]
            if("output_zerop" in kwargs.keys()):
                self.out_info["outputZp"] = kwargs["output_zerop"]
                del kwargs["output_zerop"]
            if("dtype" in kwargs.keys()):
                self.out_info["outputType"] = kwargs["dtype"]
                del kwargs["dtype"]
            if("layout" in kwargs.keys()):
                self.layout = kwargs["layout"]
                del kwargs["layout"]
            if("num_outputs" in kwargs.keys()):
                self.num_outputs = kwargs["num_outputs"]
                del kwargs["num_outputs"]

            self.out_info["outputType"] = mu.get_media_dtype(
                self.out_info["outputType"])
            self.params = self.schema.updateparams(**kwargs)
            self.guid = self.schema.getGuid()
            self.op_class = self.schema.getOpClass()
            self.cparams = self.schema.getCParams()

        def __call__(self, *inputs, **kwargs):
            """
            Callable class method which generates the input and output nodes of the operator.

            """
            minInps = self.schema.getMinInputs()
            maxInps = self.schema.getMaxInputs()
            inputs = list(inputs)
            if(len(inputs) < minInps or len(inputs) > maxInps):
                raise RuntimeError("input count mismatch")
            op = self.op_class(self.opname, self.guid,
                               self.device, inputs, self.params, self.cparams,
                               self.out_info)
            op.gen_output_tensors(self.num_outputs)
            return op.get_output_tensors()

    operator.__name__ = str(name)
    return operator


operators = s.get_operators_list()
module = sys.modules[__name__]
for op in operators:
    op_class = operator_add(op)
    op_class.__module__ = module.__name__
    setattr(module, op, op_class)
