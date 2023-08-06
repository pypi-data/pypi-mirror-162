from habana_frameworks.mediapipe.backend.nodes import opnode_tensor_info
from habana_frameworks.mediapipe.operators.media_nodes import MediaReaderNode
from habana_frameworks.mediapipe.media_types import dtype as dt
from habana_frameworks.mediapipe.media_types import readerOutType as ro
from habana_frameworks.mediapipe.backend.utils import get_numpy_dtype
import numpy as np
import os
import pathlib
import time


# temporary reader for testing
def gen_class_list(dir):
    data_dir = pathlib.Path(dir)
    return np.array(sorted(
        [item.name for item in data_dir.glob('*') if item.is_dir() == True]))


def gen_image_list(dir, format):
    img_lst = [
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n07753275/n07753275_26950.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_5088.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_549.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_5590.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_6603.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_6573.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_4713.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_582.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_3716.JPEG",
        "/software/data/pytorch/imagenet/ILSVRC2012/train/n04548280/n04548280_4635.JPEG"]
    # return np.array(sorted(glob.glob(dir + "/*/*")))
    return np.array(sorted(img_lst))


def gen_label_list(file_list, class_names, meta_dtype):
    label_list = np.array([])
    # since labels are ordered we will have use of this
    idx = 0
    for f in file_list:
        cls_name = os.path.basename(os.path.dirname((f)))
        while(idx < len(class_names)):
            if not (cls_name == class_names[idx]):
                idx = idx + 1
            else:
                break
        if (idx >= len(class_names)):
            print("idx {} len(class_names) {} ".format(idx, len(class_names)))
            raise RuntimeError("optimization error")
        label_list = np.append(label_list, idx)
    #label_list = np.array(label_list, dtype=np.uint64)
    #label_list = np.array(shape=[lfl], dtype=np.int32)
    metadata_dtype_np = get_numpy_dtype(meta_dtype)
    label_list = np.array(label_list, dtype=metadata_dtype_np)
    return label_list


def get_max_file(img_list):
    return max(img_list, key=lambda x: os.stat(x).st_size)


class read_image_jpeg_sanity(MediaReaderNode):
    """
    Class defining sanity read image node.

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
        self.dir = "/software/data/pytorch/imagenet/ILSVRC2012/train/"
        self.shuffle = params['shuffle']
        self.seed = params['seed']
        self.max_file = params['max_file']
        self.drop_remainder = params['drop_remainder']
        self.pad_remainder = params['pad_remainder']
        self.format = params['format']
        print("Finding classes ...", end=" ")
        self.class_list = gen_class_list(self.dir)
        print("Done!")
        print("Finding images ...", end=" ")
        self.img_list = gen_image_list(self.dir, self.format)
        print("Done!")
        print("Generating labels ...", end=" ")
        self.metadata_dtype = params["label_dtype"]
        self.lbl_list = gen_label_list(
            self.img_list, self.class_list, self.metadata_dtype)
        print("Done!")
        self.num_imgs = len(self.img_list)
        print("Total images/labels {} classes {}".format(self.num_imgs,
              len(self.class_list)))
        #self.shuffle_idx = np.arange(len(self.img_list))
        self.iter_loc = 0
        if self.num_imgs == 0:
            raise ValueError("image list is empty")
        if (self.seed == None):
            self.seed = int(time.time())
        if(self.max_file == None):
            print("Finding largest file ...")
            self.max_file = get_max_file(self.img_list)
        print("largest file is ", self.max_file)
        self.shuffle_idx = np.arange(self.num_imgs)
        self.num_batches = int(self.num_imgs / self.batch_size)
        self.num_imgs_slice = self.num_imgs
        self.img_list_slice = self.img_list
        self.lbl_list_slice = self.lbl_list
        self.rng = np.random.default_rng(self.seed)

    def set_params(self, params):
        """
        Setter method to set mediapipe specific params.

        :params params: mediapipe params of type "opnode_params".
        """
        self.batch_size = params.batch_size
        if(self.drop_remainder == False):
            self.roundup_filelist_labellist()
        else:
            self.rounddown_filelist_labellist()
        if not (len(self.img_list_slice) == len(self.lbl_list_slice)):
            print(self.num_imgs_slice, len(self.lbl_list_slice))
            raise ValueError("image list is not same as label list !!!")
        self.num_imgs_slice = len(self.img_list_slice)
        self.shuffle_idx = np.arange(self.num_imgs_slice)
        self.num_batches = int(self.num_imgs_slice / self.batch_size)

    def gen_output_info(self):
        """
        Method to generate output type information.

        :returns : output tensor information of type "opnode_tensor_info".
        """
        out_info = []
        o = opnode_tensor_info(dt.NDT, np.array(
            [self.batch_size], dtype=np.uint32), "")
        out_info.append(o)
        o = opnode_tensor_info(self.metadata_dtype, np.array(
            [self.batch_size], dtype=np.uint32), "")
        out_info.append(o)
        return out_info

    def get_largest_file(self):
        """
        Method to get largest media in the dataset.

        returns: largest media element in the dataset.
        """
        return self.max_file

    def get_media_output_type(self):
        return ro.FILE_LIST

    def __len__(self):
        """
        Method to get dataset length.

        returns: length of dataset in units of batch_size.
        """
        return self.num_batches

    def __iter__(self):
        """
        Method to initialize iterator.

        """
        if(self.shuffle == True):
            print("Shuffling ...",  end=" ")
            self.rng.shuffle(self.shuffle_idx)
            self.img_list_slice = self.img_list_slice[self.shuffle_idx]
            self.lbl_list_slice = self.lbl_list_slice[self.shuffle_idx]
            print("Done!")
        self.iter_loc = 0
        return self

    def __next__(self):
        """
        Method to get one batch of dataset ouput from iterator.

        """
        if self.iter_loc > (self.num_imgs_slice - 1):
            raise StopIteration
        start = self.iter_loc
        end = self.iter_loc + self.batch_size
        img_list = self.img_list_slice[start:end]
        lbl_list = self.lbl_list_slice[start:end]
        self.iter_loc = self.iter_loc + self.batch_size
        # for i in range(self.batch_size):
        #    print("{} {}".format(i,img_list[i]))
        return img_list, lbl_list

    def roundup_filelist_labellist(self):
        append_cnt = int((self.num_imgs_slice + self.batch_size - 1) /
                         self.batch_size) * self.batch_size - self.num_imgs_slice
        if(self.pad_remainder == False):
            idx = np.random.default_rng().choice(
                self.num_imgs_slice, size=append_cnt, replace=False)
            idx = sorted(idx)
        else:
            meta_dtype_np = get_numpy_dtype(self.metadata_dtype)
            idx = np.zeros(shape=(append_cnt), dtype=meta_dtype_np)
            idx = idx + len(self.img_list_slice) - 1
        img_list_pad = self.img_list_slice[idx]
        lbl_list_pad = self.lbl_list_slice[idx]
        self.img_list_slice = np.append(self.img_list_slice, img_list_pad)
        self.lbl_list_slice = np.append(self.lbl_list_slice, lbl_list_pad)
        self.num_imgs_slice = len(self.img_list_slice)

    def rounddown_filelist_labellist(self):
        slice_end = int((self.num_imgs_slice) /
                        self.batch_size) * self.batch_size
        self.img_list_slice = self.img_list_slice[0: slice_end]
        self.lbl_list_slice = self.lbl_list_slice[0: slice_end]
        self.num_imgs_slice = len(self.img_list_slice)
