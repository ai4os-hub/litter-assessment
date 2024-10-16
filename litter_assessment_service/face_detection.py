import os
import dlib
import numpy as np
import tempfile
from PIL import Image
from litter_assessment_service import imageslicer

# load CNN face detection model
wd = os.getcwd()
model_name='litter-assessment/models/mmod_human_face_detector.dat'
path = os.path.join(wd, model_name)
cnn_face_detector = dlib.cnn_face_detection_model_v1(path)

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
    col = int(tile / grid_col_len + 1)
    row = int(tile - (col - 1) * grid_col_len)
    col_glob = (row) * 128
    row_glob = (col - 1) * 128
    top_glob, bottom_glob = row_glob, 128 + row_glob
    left_glob, right_glob = col_glob, 128 + col_glob

    return top_glob, right_glob, bottom_glob, left_glob

def analyse_tiles_batch(tiles, tile_nums, global_image, grid_col_len, num_faces):
    # Convert each tile in the batch to a numpy array for processing
    img_arrays = [np.array(tile) for tile in tiles]

    # Use dlib face detection in batch mode
    dets_batch = cnn_face_detector(img_arrays, upsample_num)

    # Process the results for each tile in the batch
    for tile_num, dets in zip(tile_nums, dets_batch):
        for d in dets:
            score = d.confidence
            if score >= threshold_score:
                num_faces += 1
                top_glob, right_glob, bottom_glob, left_glob = get_tile_coordinates(tile_num, grid_col_len)
                global_image.paste((0, 0, 0), (left_glob, top_glob, right_glob, bottom_glob))
                print(f'global coordinates: {(top_glob, right_glob, bottom_glob, left_glob)}')

    return num_faces, global_image

# iterate over images in directory
def anonymize_images(image_file, image_names):
    print(f'starting anonymize_images now')
    dir = tempfile.mkdtemp()

    batch_size = 8  # You can adjust this to suit your hardware

    for count, image_path in enumerate(image_file):
        num_faces = 0
        image_name = image_names[count]

        image = Image.open(image_path)
        img = image.convert("RGB")

        shape = img.size
        x, grid = imageslicer.imageslicer_modelinput(image_path, 128, file_format='JPG', cut_im_sect=None, image_size_PLD=None)
        grid_row_len, grid_col_len = grid
        number_tiles = x.shape[0]

        # Prepare batches of tiles
        tile_batch = []
        tile_nums = []

        print(f'starting to iterate over tiles now')
        for i in range(number_tiles):
            tile = x[i, :, :, :]
            tile = np.multiply(tile, 255).astype('uint8')
            tile_image = Image.fromarray(tile)
            tile_batch.append(tile_image)
            tile_nums.append(i)

            # If batch size is reached or last tile, process the batch
            if len(tile_batch) == batch_size or i == number_tiles - 1:
                print(f'Processing batch of {len(tile_batch)} tiles...')
                num_faces, img = analyse_tiles_batch(tile_batch, tile_nums, img, grid_col_len, num_faces)

                # Clear the batch for next round
                tile_batch = []
                tile_nums = []

            if rotate:
                rotated_batch_90 = [rotate_90(tile) for tile in tile_batch]
                rotated_batch_180 = [rotate_180(tile) for tile in tile_batch]

                # Process rotated 90-degree tiles
                num_faces, img = analyse_tiles_batch(rotated_batch_90, tile_nums, img, grid_col_len, num_faces)

                # Process rotated 180-degree tiles
                num_faces, img = analyse_tiles_batch(rotated_batch_180, tile_nums, img, grid_col_len, num_faces)

        if num_faces > 0:
            path = f'{dir}/{image_name}.jpg'
            img.save(path)
            image_file[count] = path

    return image_file
