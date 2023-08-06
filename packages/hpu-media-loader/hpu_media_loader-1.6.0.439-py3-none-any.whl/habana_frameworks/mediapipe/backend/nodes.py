from habana_frameworks.mediapipe.backend.utils import get_numpy_dtype, is_valid_dtype, is_valid_layout
from abc import ABC, abstractmethod
import numpy as np

counter = 0


def node_counter():
    """
    Method generating node count information.

    :returns : counter value.
    """
    global counter
    c = counter
    counter = counter + 1
    return c

# tensor node


class TensorNode(object):
    """
    Class defining media tensor.

    """

    def __init__(self, name, src_port=0, src_op=None):
        """
        Constructor method.

        :params name: tensor name.
        :params src_port: output port number of source node.
        :params src_op: source op node.
        """
        self.name = name
        self.src_op = src_op
        self.dst_op = []
        self.src_port = src_port
        self.__data__ = None
        self.shape = None
        self.dtype = None
        self.np_shape = None
        self.np_dtype = None
        self.size = 0
        self.layout = ""
        self._pending_read_tokens_ = 0  # token based system for safe memory handling

    def data_write(self, data):
        """
        Method to write data to tensor node.

        :params data: data to be written to tensornode.
        """
        if(self._pending_read_tokens_ != 0):
            raise RuntimeError("output of {}[{}] written before its consumed".format(
                self.src_op.name, self.src_port))
        self.__data__ = data
        self._pending_read_tokens_ = len(self.dst_op)

    def data_read(self):
        """
        Method to read data to tensor node.

        :returns : data present in tensornode.
        """
        if(self._pending_read_tokens_ == 0):
            raise RuntimeError("output of {}[{}] read more then its produced".format(
                self.src_op.name, self.src_port))
        self._pending_read_tokens_ = self._pending_read_tokens_ - 1
        return self.__data__

    def check_data_avaiable(self):
        """
        Method to check data is avaiable to be read from tensor node.

        :params data: data to be written to tensornode.
        """
        if(self._pending_read_tokens_ > 0):
            return True
        else:
            return False

    def clear_data(self):
        """
        Method to clear data in tensor node.

        """
        self._pending_read_tokens_ = 0
        self.__data__ = None


class OpNode(ABC):
    """
    Abstract class defining media operator node.

    """

    def __init__(self, name, guid, device, input_tensors, params, cparams, out_info):
        """
        Constructor method.

        :params name: node name.
        :params guid: guid of node.
        :params guid: device on which this node should execute.
        :params params: node specific params.
        :params cparams: backend params.
        :params out_info: node output information
        """
        self.counter = node_counter()
        self.device = device
        #self._name = "__"+type(op).__name__+"_"+str(self._counter)
        # underscore not supported
        self.name = name + str(self.counter)
        self.opname = name
        self.output_tensors = []
        self.input_tensors = input_tensors
        self.params = params
        self.cparams = cparams
        self.guid = guid
        self.c_out_info = out_info
        self.batch_size = 1

    def gen_output_tensors(self, num_output_tensors):
        """
        Method to generate output tensors for media node.

        :params num_output_tensors: number of output tensors of the node.
        """
        for i in range(num_output_tensors):
            output_tensor_name = self.name
            if num_output_tensors > 1:
                #output_name += "[{}]".format(i)
                output_tensor_name += "o" + str(i)
            n = TensorNode(output_tensor_name, i, self)
            self.output_tensors.append(n)

    def populate_output_tensors(self, output_tensors):
        """
        Method to populate output tensors for media node.

        :params output_tensors: list of output tensors of the node.
        """
        for o in output_tensors:
            self.output_tensors.append(o)

    def _add_dynamic_outputs_(self, op, num_dyn_out):
        """
        Method to dynamically add output tensors for media node.

        :params op: opnode.
        :params num_dyn_out: number of dynamic output tensors of the node.
        """
        num_new_outputs = num_dyn_out
        num_curr_outputs = len(op.output_tensors)
        for i in range(num_curr_outputs, num_curr_outputs+num_new_outputs):
            output_name = self.name
            output_name += "do" + str(i)
            n = TensorNode(output_name, i, self)
            self.output_tensors.append(n)

    def get_output_tensors(self):
        """
        Getter method to get output tensors for media node.

        :returns : output tensor of the node.
        """
        if len(self.output_tensors) == 1:
            return self.output_tensors[0]
        else:
            return self.output_tensors

    def get_input_tensors(self):
        """
        Getter method to get input tensors for media node.

        returns: list of input tensors of the node.
        """
        return self.input_tensors

    def fetch_input_buffers(self):
        """
        Method to fetch input buffers for media node.

        returns: list of input buffers of the node.
        """
        inputs = []
        for i in self.input_tensors:
            # inputs.append(i.__data__.pop(0))
            inputs.append(i.data_read())
        return inputs

    def push_output_buffers(self, out_buffers):
        """
        Method to put output buffers for media node.

        :params out_buffers: list of output buffers of the node.
        """
        t = type(out_buffers)
        if t is tuple or t is list:
            for i in range(len(out_buffers)):
                self.output_tensors[i].data_write(out_buffers[i])
        else:
            self.output_tensors[0].data_write(out_buffers)

    def generate_node_info(self, params):
        """
        Method to generate node information.

        :params params: mediapipe params of type opnode_params.
        """
        self.set_params(params)
        out_info = self.gen_output_info()
        if(out_info == None):
            raise ValueError("out info of node {} is None".format(self.opname))
        if(not isinstance(out_info, list)):
            out_info = [out_info]
        if(len(out_info) != len(self.output_tensors)):
            raise ValueError(
                "out info incomplete for node {}".format(self.opname))
        for i in range(len(out_info)):
            o = out_info[i]
            if(not isinstance(o, opnode_tensor_info)):
                raise ValueError(
                    "operator {}  return output info is not opnode_tensor_info type".format(self.opname))
            if(not isinstance(o.shape, np.ndarray)):
                raise ValueError(
                    "operator {} port {} return shape is not numpy array".format(self.opname, i))
            if(not (np.uint32 == o.shape.dtype)):
                raise ValueError(
                    "operator {} port {} return shape is not uint32 dtype".format(self.opname, i))
            if(len(o.shape) > 5):
                raise ValueError(
                    "output shape from {} port {} is greater then 5".format(self.opname, i))
            if(len(o.shape) < 1):
                raise ValueError(
                    "output shape from {} port {} is less then one".format(self.opname, i))
            if(not is_valid_dtype(o.dtype)):
                raise ValueError(
                    "operator {} port {} return dtype is not in media_type.dtype".format(self.opname, i))
            if(not is_valid_layout(o.layout)):
                raise ValueError(
                    "operator {} port {} return layout is not in media_type.layout".format(self.opname, i))
            self.output_tensors[i].shape = out_info[i].shape
            self.output_tensors[i].np_shape = out_info[i].shape[::-1]
            self.output_tensors[i].dtype = out_info[i].dtype
            self.output_tensors[i].np_dtype = get_numpy_dtype(
                out_info[i].dtype)
            self.output_tensors[i].layout = out_info[i].layout
            self.output_tensors[i].size = 1
            for j in range(len(self.output_tensors[i].shape)):
                self.output_tensors[i].size = self.output_tensors[i].size * \
                    self.output_tensors[i].shape[j]

    @abstractmethod
    def set_params(self, params):
        """
        Abstract setter method to set mediapipe specific params.

        :params params: mediapipe params of type "media_ext_reader_op_params".
        """
        pass

    @abstractmethod
    def gen_output_info(self):
        """
        Abstract method to generate output type information.

        :returns : output tensor information of type "media_ext_reader_op_tensor_info".
        """
        pass


class opnode_params(object):
    """
    Class defining param information sent to external reader op class.

    """

    def __init__(self, batch_size):
        """
        Constructor method.

        :params batch_size: Batch size.
        """
        self.batch_size = batch_size


class opnode_tensor_info(object):
    """
    Class defining return numpy tensor information of external cpu op class.

    """

    def __init__(self, dtype, shape, layout):
        """
        Constructor method.

        :params dtype: output data type.
        :params shape: output shape.
        :params layout: output layout.
        """
        self.dtype = dtype
        self.shape = shape
        self.layout = layout
