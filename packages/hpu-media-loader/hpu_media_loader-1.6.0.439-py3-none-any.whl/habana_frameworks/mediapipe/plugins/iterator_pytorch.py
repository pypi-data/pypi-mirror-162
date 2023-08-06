import torch
import habana_frameworks.torch.utils.experimental as htexp
from habana_frameworks.mediapipe.backend.iterator import _MediaIterator
from habana_frameworks.mediapipe.media_proxy import HPUProxy
from habana_frameworks.mediapipe.media_types import dtype as dt
import media_pipe_proxy as mppy

from ctypes import *


# dictionary to convert media data type to torch data type.
to_torch_dtype = {dt.INT8: torch.int8,
                  dt.UINT8: torch.uint8,
                  dt.INT16: torch.int16,
                  dt.UINT16: torch.int16,
                  dt.FLOAT32: torch.float32,
                  dt.INT32: torch.int32,
                  dt.UINT32: torch.int32,
                  dt.INT64: torch.int64,
                  dt.UINT64: torch.int64
                  }


class HPUDevice:
    """
    Class defining hpu device.

    """

    def __init__(self, device, device_id):
        """
        Constructor method.

        :params device: device on which mediapipe is to be run. <hpu>
        :params device_id: device id.
        """
        if device != 'hpu':
            raise RuntimeError("device {} not supported!".format(device))

        self.device_id = device_id
        self.name = 'Gaudi2'

    def release_device(self, device_id):
        """
        Method to release device.

        :params device_id: device id to release.
        """
        if self.device_id != device_id:
            assert False, "Error: Invalid device_id {} for release_device".format(
                self.device_id)

    def get_device_id(self):
        """
        Method to get device ID.

        :returns : device id.
        """
        return self.device_id

    def get_device_name(self):
        """
        Method to get device name.

        :returns : device name.
        """
        return self.name

    # def __del__(self):
    #    print("HPUDevice destructor")


class PytorchDevice(HPUProxy):
    """
    Class specific to pytorch framework, derived from HPU Proxy.
    This provides functionality to get device id and allocate tensors

    """
    instance = None
    instanceCount = 0

    def __init__(self, name='hpu', device_id=None):
        """
        Constructor method.

        :params name: device on which mediapipe is to be run. <hpu>
        :params device_id: device id.
        """
        if PytorchDevice.instance == None:
            PytorchDevice.instance = HPUDevice(name, device_id)

        PytorchDevice.instanceCount += 1
        self.device = PytorchDevice.instance
        self.torch_device = torch.device(name)
        self.buff_dict = {}
        self.tensor_dict = {}  # TODO: May need to change to list for perf

    def __del__(self):
        """
        Destructor method.

        """
        PytorchDevice.instanceCount -= 1
        if PytorchDevice.instanceCount == 0:
            del PytorchDevice.instance

    def new_buffer(self, size):
        """
        Method for creating new buffer.

        :params size: Buffer size in bytes.
        :returns : device address of buffer.
        """
        # TODO: check torch.zeros
        tensor = torch.empty(
            tuple([size]), device=self.torch_device, dtype=torch.uint8)
        t_addr = htexp._data_ptr(tensor)
        self.buff_dict[t_addr] = tensor
        return t_addr

    # def get_data_ptr(self, tensor):
    #    return htexp._data_ptr(tensor)

    def get_compute_stream(self):
        """
        Method to get device compute stream.

        :returns : device compute stream.
        """
        compute = htexp._compute_stream()
        return compute
        # return 0  #TODO: check if not to share Compute Stream

    def new_tensor_dataptr(self, shape, dtype):
        """
        Method to get device tensor.

        :params shape: shape of tensor.
        :params dtype: datatype of tensor.
        :returns : device address of tensor.
        """
        tensor = torch.empty(
            tuple(shape), device=self.torch_device, dtype=to_torch_dtype[dtype])
        t_addr = htexp._data_ptr(tensor)
        self.tensor_dict[t_addr] = tensor
        return t_addr

    def get_tensor(self, data_ptr):
        """
        Method to get tensor from device address

        :params data_ptr: return tensor for device address
        """
        return self.tensor_dict[data_ptr]

    def delete_tensor(self, data_ptr):
        """
        Method to free allocated tensor.

        :params data_ptr: device address for which tensor is to be freed.
        """
        del self.tensor_dict[data_ptr]
        # print("pytorch delete_tensor len is ", len(self.tensor_dict), data_ptr)

    def delete_buffer(self, data_ptr):
        """
        Method for freeing buffer.

        :params data_ptr: device address to be freed.
        """
        del self.buff_dict[data_ptr]

    def flush_tensors(self, tensor_l):
        """
        Method to flush pending tensors in queue.

        :params tensor_l: list of device address for which tensors are to be flushed
        """
        # print("flush tensor ", tensor_l," pending list", self.tensor_dict.keys())
        for buffer in tensor_l:
            self.delete_tensor(buffer)

    def get_device_name(self):
        """
        Method to get device name.

        :returns : device name.
        """
        return self.device.get_device_name()

    def get_device_id(self, device_type):  # DeviceType is unused
        """
        Method to get device ID.

        :params device_type: device type. This is unused param.
        :returns : device id.
        """
        return self.device.get_device_id()

    def release_device_id(self, synDeviceId):
        """
        Method to release device.

        :params synDeviceId: device id to release.
        """
        self.device.release_device(synDeviceId)


class HPUGenericPytorchIterator(_MediaIterator):
    """
    Class defining mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        device_id = mediapipe.getDeviceId()
        self.proxy_device = PytorchDevice(name='hpu', device_id=device_id)
        # print("Device name is ",self.proxy_device.get_device_name())
        mediapipe.build()
        self.proxy_set = False
        super().__init__(_pipeline=mediapipe)

    def __iter__(self):
        """
        Method to initialize mediapipe iterator.

        :returns : iterator for mediapipe
        """
        if self.proxy_set == False:
            self.pipe.set_proxy(mppy.fwType.PYTHON_FW, self.proxy_device)
            self.proxy_set = True
        self.pipe.iter_init()
        return self

    def __next__(self):
        """
        Method to run mediapipe iterator over one batch of dataset and return the output tensors.

        :returns : output tensors.
        """
        outputs = self.pipe.run()
        output_tensors = []
        for output in outputs:
            tensor = self.proxy_device.get_tensor(output.dev_addr)
            output_tensors.append(tensor)
        return output_tensors


class HPUResnetPytorchIterator(HPUGenericPytorchIterator):
    # ToDo: check if HPUResnetPytorchIterator needed
    """
    Class defining Resnet mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe)

    def __next__(self):
        """
        Method to run mediapipe iterator over one batch of dataset and return the output tensors.

        :returns : output tensors.
        """
        images, labels = self.pipe.run()
        images_tensor = self.proxy_device.get_tensor(images.dev_addr)
        labels_tensor = self.proxy_device.get_tensor(labels.dev_addr)
        # TODO: check if labels_tensor.long() needed
        return images_tensor, labels_tensor.long()


class HPUSsdPytorchIterator(HPUGenericPytorchIterator):
    """
    Class defining SSD mediapipe iterator for Pytorch framework.
    This class provides functionality to get output tensors from mediapipe.

    """

    def __init__(self, mediapipe):
        """
        Constructor method.

        :params mediapipe: mediapipe
        """
        super().__init__(mediapipe=mediapipe)

    def __next__(self):
        """
        Method to run mediapipe iterator over one batch of dataset and return the output tensors.

        :returns : output tensors.
        """
        # lengths is not returned from iterator
        images, ids, sizes, boxes, labels, lengths, batch = self.pipe.run()

        images_tensor = self.proxy_device.get_tensor(images.dev_addr)
        ids_tensor = self.proxy_device.get_tensor(ids.dev_addr)
        sizes_tensor = self.proxy_device.get_tensor(sizes.dev_addr)
        img_size = list(torch.hsplit(sizes_tensor, 2))  # Split the tensor
        b_size = self.pipe.getBatchSize()
        img_size[0] = img_size[0].reshape(b_size)
        img_size[1] = img_size[1].reshape(b_size)

        boxes_tensor = self.proxy_device.get_tensor(boxes.dev_addr)
        labels_tensor = self.proxy_device.get_tensor(labels.dev_addr)

        batch_tensor = self.proxy_device.get_tensor(batch.dev_addr)
        # TODO: check if can be avoided
        batch_tensor_cpu = batch_tensor.to('cpu')
        batch_np = batch_tensor_cpu.numpy()
        batch = batch_np[0]

        if batch < b_size:
            images_tensor = images_tensor[:batch]
            ids_tensor = ids_tensor[:batch]
            img_size[0] = img_size[0][:batch]
            img_size[1] = img_size[1][:batch]
            boxes_tensor = boxes_tensor[:batch]
            labels_tensor = labels_tensor[:batch]

        # TODO: check if labels_tensor.long() needed
        return images_tensor, ids_tensor, img_size, boxes_tensor, labels_tensor.long()
