from habana_frameworks.mediapipe.backend.nodes import opnode_tensor_info
from habana_frameworks.mediapipe.operators.media_nodes import MediaHPUNode
from habana_frameworks.mediapipe.backend.utils import get_str_dtype
import numpy as np


class media_hpu_ops(MediaHPUNode):
    """
    Class representing media hpu node.

    """

    def __init__(self, name, guid, device, inputs, params, cparams, out_info):
        """
        Constructor method.

        :params name: node name.
        :params guid: guid of node.
        :params guid: device on which this node should execute.
        :params params: node specific params.
        :params cparams: backend params.
        :params out_info: node output information
        """
        super().__init__(
            name, guid, device, inputs, params, cparams, out_info)
        self.batch_size = 1
        self.params = params
        self.out_info = out_info
        self.dtype = get_str_dtype(out_info['outputType'])
        self.out_info = opnode_tensor_info(
            self.dtype, np.array([0], dtype=np.uint32), "")

    def set_params(self, params):
        """
        Setter method to set mediapipe specific params.

        :params params: mediapipe params of type "opnode_params".
        """
        pass

    def gen_output_info(self):
        """
        Method to generate output type information.

        :returns : output tensor information of type "opnode_tensor_info".
        """
        return self.out_info
