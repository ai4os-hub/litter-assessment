import os
import dlib
import numpy as np
import tempfile
import pickle

from PIL import Image
from litter_assessment_service import imageslicer


# load CNN face detection model
cnn_face_detector = dlib.cnn_face_detection_model_v1('litter-assessment/models/mmod_human_face_detector.dat')

upsample_num = 1
rotate = True
threshold_score = 0.5

def rotate_90(image):
    rotated_image = image.rotate(-90, expand=True)
    return rotated_image

def rotate_180(image):
    rotated_image = image.rotate(180, expand=True)
    return rotated_image

def get_tile_coordinates(tile, grid_col_len):
    col = int(tile/grid_col_len +1)
    row = int(tile - (col - 1)*grid_col_len)
    col_glob = (row) * 128
    row_glob = (col-1) * 128
    top_glob, bottom_glob = row_glob, 128+row_glob
    left_glob, right_glob = col_glob, 128+col_glob

    return top_glob, right_glob, bottom_glob, left_glob

def analyse_tile(image, num_faces, tile_num, global_image, grid_col_len):
    img_array = np.array(image)
    dets = cnn_face_detector(img_array, upsample_num)

    for j, d in enumerate(dets):
        score = d.confidence
        if score >= threshold_score:
            num_faces += 1
            top_glob, right_glob, bottom_glob, left_glob = get_tile_coordinates(tile_num, grid_col_len)
            global_image.paste((0, 0, 0), (left_glob, top_glob, right_glob, bottom_glob))
            print(f'global coordinates: {(top_glob, right_glob, bottom_glob, left_glob)}')

    return num_faces, global_image

# iterate over images in directory
def anonymize_images(image_file, image_names):
    dir = tempfile.mkdtemp()
    for count, image_path in enumerate(image_file):
        #print(f'This is the image in image_file: {image_path}')
        #print(f'This count {count} is in image_file[count] {image_file[count]}')

        num_faces = 0
        image_name = image_names[count]

        image = Image.open(image_path)
        img = image.convert("RGB")

        shape = img.size
        x, grid = imageslicer.imageslicer_modelinput(image_path, 128, file_format='JPG', cut_im_sect=None, image_size_PLD=None)
        grid_row_len, grid_col_len = grid
        number_tiles = x.shape[0]

        # run face detection on every sliced image tile
        for i in range(number_tiles):
            tile = x[i, :, :, :]
            tile = np.multiply(tile, 255).astype('uint8')
            tile_image = Image.fromarray(tile)
            tile_num = i

            num_faces, img = analyse_tile(tile_image, num_faces, tile_num, img, grid_col_len)

            if rotate:
                tile_rotated_90 = rotate_90(tile_image)
                num_faces, img = analyse_tile(tile_rotated_90, num_faces, tile_num, img, grid_col_len)

                tile_rotated_180 = rotate_180(tile_image)
                num_faces, img = analyse_tile(tile_rotated_180, num_faces, tile_num, img, grid_col_len)

        #print(f'Number of faces in this image: {num_faces}')
        if num_faces > 0:
            path = f'{dir}/{image_name}.jpg'
            img.save(path)
            image_file[count] = path

    return image_file
