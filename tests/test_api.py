# -*- coding: utf-8 -*-
"""
Its good practice to have tests checking your code runs correctly.
Here we included a dummy test checking the api correctly returns
expected metadata. We suggest to extend this file to include, for
example, test for checking the predict() function is indeed working
as expected.

These tests will run in the Jenkins pipeline after each change
you make to the code.

It is good to use either unittest or pytest 
"""
import sys
import os
import shutil
import unittest
import requests
import tarfile
import logging

from deepaas.model.v2.wrapper import UploadedFile
from litter_assessment_service import api
from litter_assessment_service import preprocessing

BASE_PATH = os.path.dirname(os.path.normpath(os.path.dirname(__file__)))
TEST_PATH = os.path.join(BASE_PATH, "tests")

def test_get_metadata():
    meta = api.get_metadata()
    assert type(meta) is dict

def test_predict_single_im():
    test_data_path=os.path.join(TEST_PATH,'data','samples')
    file_path=os.path.join(test_data_path, 'test_image.png')
    tmp_fpath = os.path.join(test_data_path, 'tmp_file.jpg')
    shutil.copyfile(file_path, tmp_fpath)
    file = UploadedFile(name='data', filename=tmp_fpath, content_type='image/jpg', original_filename='test_image')
    kwargs = {'files': file, 'PLD_plot': True, 'PLQ_plot': True}
    api.predict(**kwargs)

def test_predict_zip():
    test_data_path=os.path.join(TEST_PATH, 'data','samples')
    file_path=os.path.join(test_data_path, 'test_images.zip')
    tmp_fpath = os.path.join(test_data_path, 'tmp_file.zip')
    shutil.copyfile(file_path, tmp_fpath)
    file = UploadedFile(name='data', filename=tmp_fpath, content_type='application/zip', original_filename='test_zip')
    kwargs = {'files': file, 'PLD_plot': True, 'PLQ_plot': True}
    api.predict(**kwargs)

def test_predict_bytes():
    test_data_path=os.path.join(TEST_PATH, 'data','samples')
    file_path=os.path.join(test_data_path, 'test_image.png')
    image=open(os.path.join(os.getcwd(), 'test_images', file_path), 'rb')
    bin_image = image.read()
    file = UploadedFile(name='data', filename=bin_image, content_type='application/octet-stream', original_filename='test_image.JPG')
    kwargs = {'files': file, 'PLD_plot': True, 'PLQ_plot': True}
    api.predict(**kwargs)

def download_file(url):
    local_filename = url.split('/')[-1] # OR add the path, e.g. BASE_PATH/models
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

def main():
    # just python logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # URL to the models file
    models_url = "https://share.services.ai4os.eu/index.php/s/HQmXS7mcDK82sz3/download/models.tar.gz"

    try:
    # call download_file function
        models_archived = download_file(models_url)

        # dearchive downloaded .tar.gz file
        with tarfile.open(models_archived, 'r:gz') as ms:
            ms.extractall("./") # OR use BASE_PATH/models

        # may delete the *tar.gz afterwards
        os.remove(models_archived)
    except Exception as err:
        logging.error(f"Unexpected {err=}, {type(err)=}")

    test_get_metadata()
    test_predict_bytes()
    test_predict_zip()
    test_predict_single_im()

if __name__=='__main__':
    main()
