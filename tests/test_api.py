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

from deepaas.model.v2.wrapper import UploadedFile
from litter_assessment_service import api

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

def main():
    test_get_metadata()
    test_predict_bytes()
    test_predict_zip()
    test_predict_single_im()

if __name__=='__main__':
    main()
