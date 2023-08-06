
# INFO: Here we will give params and its default arguments order doesnt matter
# INFO: if any parameter is not set here it will be set to zero
empty_params = {}

resize_params = {
    'mode': 1,
    'scaleDim1': 0,
    'scaleDim2': 0,
    'scaleDim3': 0,
    'coordTransMode': 0,
    'nearestMode': 0,
    'excludeOutside': False,
    'useScales': False,
    'cubicCoeffA': 0,
    'size1': 0,
    'size2': 0,
    'size3': 1
}

random_bernoulli_params = {
    'seed': 100
}

# color_space_modes defined in trees/npu-stack/specs_external/perf_lib_layer_params.h
color_space_modes = {
    'RGB_TO_YCBCR': 0,
    'RGB_TO_BGR': 1,
    'YCBCR_TO_RGB': 2,
    'YCBCR_TO_BGR': 3,
    'BGR_TO_RGB': 4,
    'BGR_TO_YCBCR': 5,
    'GRAY_TO_RGB': 6,
    'GRAY_TO_BGR': 7,
    'GRAY_TO_YCBCR': 8,
    'RGB_TO_GRAY': 9,
    'YCBCR_TO_GRAY': 10,
    'BGR_TO_GRAY': 11
}
color_space_params = {
    'colorSpaceMode': color_space_modes['RGB_TO_BGR']
}

crop_params = {
    'crop_w': 100,
    'crop_h': 100,
    'crop_d': 0,
    'crop_pos_x': 0.,
    'crop_pos_y': 0.,
    'crop_pos_z': 0,
    'pad_val': 0,
}

cmn_params = {
    'mirror': 0,
    'crop_w': 100,
    'crop_h': 100,
    'crop_d': 0,
    'crop_pos_x': 0.,
    'crop_pos_y': 0.,
    'crop_pos_z': 0,
    'pad_val': 0,
}

reshape_params = {
    'size': [0, 0, 0, 0, 0],
    'tensorDim': 5,
}

contrast_params = {
    'contrast_scale': 0.0
}

brightness_params = {
    'brightness_scale': 0.0
}

saturation_params = {
    'saturation_level': 0.0
}

transpose_params = {
    'permutation': [0, 1, 2, 3, 4],
    'tensorDim': 5}

slice_params = {
    'axes': [0, 0, 0, 0, 0],
    'starts': [0, 0, 0, 0, 0],
    'ends': [0, 0, 0, 0, 0],
    'steps': [0, 0, 0, 0, 0]
}

cast_params = {
    'round_mode': 0
}

flip_params = {
    "horizontal": 0,
    "vertical": 0,
    "depthwise": 0
}

normalize_params = {
    "scale": 0.0,
    "shift": 0.0,
    "axis": 0,
    "batch": False
}

hue_params = {
    "degree": 0
}

# ToD: To add
image_rotate_params = {
    "m_angle": 90.,
    "m_inputCenterX": 0,
    "m_inputCenterY": 0,
    "m_outputCenterX": 0,
    "m_outputCenterY": 0,
    "m_background": 0
}

frr_params = {
    "frrRatio": 1.0
}
