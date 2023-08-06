from habana_frameworks.mediapipe.media_types import dtype as dt

# INFO: Here we will give params and its default arguments order doesnt matter
# INFO: if any parameter is not set here it will be set to zero

media_ext_reader_op_params = {
    'impl': None,
    'seed': 0,
    'priv_params': {}  # user defined params can be passed here
}

read_image_from_dir_params = {
    'dir': "/",
    'format': "jpg",
    'shuffle': True,
    'seed': None,
    'max_file': None,
    'drop_remainder': False,
    'pad_remainder': False,
    'label_dtype': dt.UINT64,
    'num_slices': 1,
    'slice_index': 0
}

coco_reader_params = {
    'root':         "",
    'annfile':   "",
    'drop_remainder': False,
    'pad_remainder': False,
    'num_slices': 1,
    'slice_index': 0,
    'shuffle': True,
    'max_file': None,
    'partial_batch': False,
    'seed': None,
}


ssd_metadata_params = {
    'crop_iterations':  1,
    'batch_size':       1,
    'flip_probability': 0.5,
    'seed':             0,
    'dboxes':           None
}
