# main mediapipe file : master controller
from habana_frameworks.mediapipe.backend.utils import get_media_fw_type
from habana_frameworks.mediapipe.backend.utils import getDeviceIdFromDeviceName
from habana_frameworks.mediapipe.backend.graph import graph_executor, graph_processor
from habana_frameworks.mediapipe.operators.media_nodes import media_layout as cl
from habana_frameworks.mediapipe.backend.iterator import HPUGenericIterator as iter
from habana_frameworks.mediapipe.media_types import layout as lt
from habana_frameworks.mediapipe.backend.proxy_impl import set_c_proxy, del_c_proxy
import media_pipe_types as mpt
import media_pipe_proxy as mppy  # NOQA
from abc import ABC, abstractmethod
import numpy as np


class MediaPipe(ABC):
    """
    Abstract class representing media pipe.

    """
    @abstractmethod
    def __init__(self, device=None, prefetch_depth=2, batch_size=1, channel=3, height=None, width=None, pipename=None, layout=lt.NHWC):
        """
        Constructor method.

        :params device: media device to run mediapipe on. <hpu/hpu:0>
        :params prefetch_depth: mediapipe prefetch count. <1/2/3>
        :params batch_size: mediapipe output batch size.
        :params channel: mediapipe output channel.
        :params height: mediapipe output height.
        :params width: mediapipe output width.
        :params pipename: mediapipe user defined name.
        :params layout: mediapipe output layout. <lt.NHWC/lt.WHCN>

        """
        self._batch_size_ = batch_size
        self._queue_depth_ = prefetch_depth
        self._img_cwhb_ = np.array([channel, width, height, batch_size])
        self._img_out_ = self._img_cwhb_[cl.idx[cl.enum[layout]]]
        self._graph_compiled_ = False
        self._pipeline_init_ = False
        self._device_ = device
        self._num_outstanding_cmd_ = 0
        self._batch_number_ = 0
        self._device_id_ = getDeviceIdFromDeviceName(device)
        print("MediaPipe device {} device_id {} pipename {}".format(
            device, self._device_id_, pipename))
        self._pipename_ = pipename
        self._fw_type_ = mppy.fwType.SYNAPSE_FW
        self._proxy_ = 0x0  # this must be 0 and not None
        self._python_proxy_ = None
        # INFO: as of now only 1 recipe is supported
        self._iter_repeat_count_ = 1
        self._cold_run_ = True
        print("{}  created.".format(self._pipename_))

    def __del__(self):
        """
        Destructor method.

        """
        self.del_iter()
        print("closing mediapipe : ", self._pipename_)

    @abstractmethod
    def definegraph(self):
        """
        Abstract method defining the media graph.
        Derived class defines the control flow of the media nodes in this method.

        """
        pass

    def setOutputShape(self, batch_size, channel, height, width, layout=lt.NHWC):
        """
        Setter method to set media pipe output shape.

        :params channel: mediapipe output channel.
        :params height: mediapipe output height.
        :params width: mediapipe output width.
        :params layout: mediapipe output layout. <lt.NHWC/lt.WHCN>
        """
        self._img_cwhb_ = np.array(
            [channel, width, height, batch_size], dtype=np.uint32)
        self._img_out_ = self._img_cwhb_[cl.idx[cl.enum[layout]]]

    def getDeviceId(self):
        """
        Getter method to get media pipe device id

        :returns : mediapipe device id.
        """
        return self._device_id_

    def getBatchSize(self):
        """
        Getter method to get media pipe batch_size

        :returns : mediapipe batch_size.
        """
        return self._batch_size_

    def build(self):
        """
        Method to build media pipe nodes and generate the recipe.

        """
        if(self._graph_compiled_ == True):
            # graph already built
            return
        self._graph_compiled_ = True
        # call user defined graph function
        output_tensors = self.definegraph()
        if isinstance(output_tensors, tuple):
            output_tensors = list(output_tensors)
        elif not isinstance(output_tensors, list):
            output_tensors = [output_tensors]
        # below code is injecting output shape in the last media node
        output_tensors[0].src_op.out_info.shape = np.array(
            self._img_out_, dtype=np.uint32)
        self._gp_ = graph_processor(self._device_, output_tensors)
        self._gp_.segment_graph()
        self._gp_.process_and_validate_graph(self._batch_size_)
        self._recipe_ = self._gp_.compile()

    def set_proxy(self, fw_type, proxy):
        """
        Setter method to set media proxy.

        :params fw_type: framework to be used by media. <SYNAPSE_FW/TF_FW/PYTHON_FW>
        :params proxy : c++ proxy address.
        """
        fw_type = get_media_fw_type(fw_type)
        if not isinstance(fw_type, mppy.fwType):
            raise RuntimeError(" Invalid proxy type.")
        self._fw_type_ = fw_type
        if(fw_type == mppy.fwType.PYTHON_FW):
            self._proxy_ = set_c_proxy(proxy)
            self._python_proxy_ = proxy
        else:
            self._proxy_ = proxy

    def set_repeat_count(self, count):
        """
        Setter method to set mediapipe iteration repeat count.

        :params count: number of time media pipe iteration to be repeated.
        """
        self._iter_repeat_count_ = count

    def iter_init(self):
        """
        Method to initialize mediapipe iterator.

        """
        print("{} iter init".format(self._pipename_))
        if (self._pipeline_init_ == False):
            self._gexe_ = graph_executor(self._gp_,
                                         self._queue_depth_,
                                         self._img_cwhb_,
                                         self._fw_type_,
                                         self._proxy_,
                                         self._python_proxy_)
            # TODO: mpt.device.GRECO
            self._gexe_.acquire_device(mpt.device.GAUDI2)
            self._gexe_.initialize_memory()
            self._gexe_.start_worker()
            self._pipeline_init_ = True
        else:
            self._gexe_.flush_pipeline()
        self._num_outstanding_cmd_ = 0
        self._cold_run_ = True
        self._gexe_.initialize_iter_pipeline(self._iter_repeat_count_)
        num_cmd_to_push = self._queue_depth_
        for _ in range(num_cmd_to_push):
            try:
                self._gexe_.execute_iter_pipeline()
                self._gexe_.execute_pipeline()
                self._num_outstanding_cmd_ = self._num_outstanding_cmd_ + 1
            except StopIteration:
                break

    def del_iter(self):
        """
        Method to close media iteration and release device.

        """
        if self._pipeline_init_ == True:
            print("{} iter del".format(self._pipename_))
            self._gexe_.flush_pipeline()
            self._gexe_.stop_worker()
            self._gexe_.free_memory()
            self._gexe_.release_device()
            self._pipeline_init_ = False

            if self._python_proxy_ is not None:
                del_c_proxy(self._proxy_)

    def run(self):
        """
        Method to run mediapipe iterator over one batch of dataset.

        :returns : one batch of media graph processed output.
        :raises StopIteration: when complete dataset iteration and number repeat counnt is done.
        """
        if(self._num_outstanding_cmd_ > 0):
            outputs = self._gexe_.get_output()
            self._num_outstanding_cmd_ = self._num_outstanding_cmd_ - 1
        else:
            raise StopIteration
        try:
            self._gexe_.execute_iter_pipeline()
            self._gexe_.execute_pipeline()
            self._num_outstanding_cmd_ = self._num_outstanding_cmd_ + 1
        except StopIteration:
            pass
        return outputs

    def as_iterator(self):
        """
        Method to get mediapipe iteratable object.

        :returns : mediapipe iteratable object.
        """
        if self._fw_type_ == mppy.fwType.SYNAPSE_FW:
            return iter(mediapipe=self)
        else:
            print("Pipe not iterable, use iterator")
            return None

    def get_batch_count(self):
        """
        Getter method to get media pipe number of batches in dataset.

        :returns : mediapipe number of batches presnet in dataset.
        """
        reader = self._gp_.get_reader_ops()[0]
        return len(reader)
