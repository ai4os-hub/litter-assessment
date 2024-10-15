import cv2
import os 
import dlib
import numpy as np
import tempfile
import pickle

from PIL import Image
from litter_assessment.imageslicer import imageslicer_modelinput


#load file directory and cnn model
#folder = "test_images/raw_data_philippines/test"
#image_file = os.listdir(folder)
cnn_face_detector = dlib.cnn_face_detection_model_v1('litter_assessment/models/mmod_human_face_detector.dat')

upsample_num = 1
rotate = True
threshold_score = 0.5

def rotate_90(image):
    rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return rotated_image

def rotate_180(image):
    rotated_image = cv2.rotate(image, cv2.ROTATE_180)
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
    dets = cnn_face_detector(image, upsample_num)

    for j, d in enumerate(dets):
        score = d.confidence
        if score >= threshold_score:
            num_faces += 1
            top_glob, right_glob, bottom_glob, left_glob = get_tile_coordinates(tile_num, grid_col_len)
            global_image[top_glob:bottom_glob, left_glob:right_glob] = 0
            to_print = top_glob, right_glob, bottom_glob, left_glob
            print(f'global coordinates: {to_print}')

    return num_faces, global_image

#iterate over images in directory
def anonymize_images(image_file, image_names):
    #dir = tempfile.TemporaryDirectory()
    dir = tempfile.mkdtemp()
    for count,image in enumerate(image_file):
        print(f'this is the image in image_file: {image}')
        print(f'this count {count} is in image_file[count] {image_file[count]}')
        num_faces = 0
        image_name = image_names[count]

        #file_path = os.path.join(folder, image)
        file_path = image
        img = cv2.imread(file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        shape = img.shape
        x, grid = imageslicer_modelinput(file_path, 128, file_format = 'JPG', cut_im_sect = None, image_size_PLD = None)
        grid_row_len, grid_col_len = grid
        number_tiles = x.shape[0]

        #run face detection on every sliced image tile
        for i in range(number_tiles):
            tile = x[i,:,:,:]
            tile = np.multiply(tile, 255)
            tile = tile.astype('uint8')
            tile_num = i

            num_faces, img = analyse_tile(tile, num_faces, tile_num, img, grid_col_len)
            if rotate:
                tile_rotated = rotate_90(tile)
                num_faces, img = analyse_tile(tile_rotated, num_faces, tile_num, img, grid_col_len)
                tile_rotated = rotate_180(tile)
                num_faces, img = analyse_tile(tile_rotated, num_faces, tile_num, img, grid_col_len)

        print(f'num faces in this image: {num_faces}')
        if num_faces > 0:
            im = Image.fromarray(img)
            path = f'{dir}/{image_name}.jpg'
            im.save(path)
            image_file[count] = path

        return image_file