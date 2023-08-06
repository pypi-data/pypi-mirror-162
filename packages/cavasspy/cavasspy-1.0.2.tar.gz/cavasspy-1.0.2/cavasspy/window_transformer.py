from hammer.image.transformation import transform_window


def cavass_soft_tissue_window(input_data):
    return transform_window(input_data, 1000, 500)


def cavass_bone_window(input_data):
    return transform_window(input_data, 2000, 4000)
