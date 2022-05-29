#!/usr/bin/env python3

from person_db import Person
from person_db import Face
from person_db import PersonDB
import face_recognition
import numpy as np
from datetime import datetime
import cv2
import os

import timm
import torch
from torch import nn
import numpy as np

from PIL import Image
import matplotlib.pyplot as plt

import calc


class FaceClassifier():
    def __init__(self, threshold, ratio, save_dir):
        self.similarity_threshold = threshold
        self.ratio = ratio
        self.save_dir = save_dir

    def get_face_and_cloth_image(self, frame, box):
        '''
        param:
            frame: 프레임 이미지
            box: 좌표값 (top, right, bottom, left)
        return:
            padded_face: 얼굴 이미지 (numpy array)
            padded_cloth: 옷 이미지 (numpy array)
        '''
        img_height, img_width = frame.shape[:2]
        (box_top, box_right, box_bottom, box_left) = box # 딱 얼굴 이미지
        box_width = box_right - box_left
        box_height = box_bottom - box_top
        # padding
        crop_top = max(box_top - box_height, 0)
        pad_top = -min(box_top - box_height, 0)
        crop_bottom = min(box_bottom + box_height, img_height - 1)
        pad_bottom = max(box_bottom + box_height - img_height, 0)
        crop_left = max(box_left - box_width, 0)
        pad_left = -min(box_left - box_width, 0)
        crop_right = min(box_right + box_width, img_width - 1)
        pad_right = max(box_right + box_width - img_width, 0)
        # cropping
        face_image = frame[crop_top:crop_bottom, crop_left:crop_right]
        cloth_image = frame[box_bottom+int(box_height*0.2):crop_bottom, crop_left:crop_right]
        # return
        if (pad_top == 0 and pad_bottom == 0):
            if (pad_left == 0 and pad_right == 0):
                return face_image, cloth_image
        padded_face = cv2.copyMakeBorder(face_image, pad_top, pad_bottom,
                                        pad_left, pad_right, cv2.BORDER_CONSTANT)
        padded_cloth = cv2.copyMakeBorder(cloth_image, pad_top, pad_bottom,
                                         pad_left, pad_right, cv2.BORDER_CONSTANT)

        return padded_face, padded_cloth

    def preprocess(self, image, size):
        try:
            img = Image.fromarray(image).convert('RGB').resize(size, resample=3)
            arr = np.asarray(img).astype(int)
            return arr
        except OSError as ex:
            print(f"skipping file...: {ex}")
            return None

    # return list of dlib.rectangle
    def locate_faces(self, frame):
        if self.ratio == 1.0:
            rgb = frame[:, :, ::-1]
        else:
            small_frame = cv2.resize(frame, (0, 0), fx=self.ratio, fy=self.ratio)
            rgb = small_frame[:, :, ::-1]

        boxes = face_recognition.face_locations(rgb, model='cnn') # model='cnn': use gpu in dlib

        if self.ratio == 1.0:
            return boxes

        boxes_org_size = []
        for box in boxes:
            (top, right, bottom, left) = box
            left = int(left / self.ratio)
            right = int(right / self.ratio)
            top = int(top / self.ratio)
            bottom = int(bottom / self.ratio)
            box_org_size = (top, right, bottom, left)
            boxes_org_size.append(box_org_size)

        return boxes_org_size

    def detect_faces(self, frame):
        # face locationss
        face_boxes = self.locate_faces(frame) # box: (top, right, bottom, left)
        # 사람이 2명 ~ 4명 사이일 때만 수행
        if len(face_boxes) <= 1 or len(face_boxes) >= 5:
            return None

        # faces found
        faces = []
        now = datetime.now()
        str_ms = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '-'

        # face_encodings
        '''
        Given an image, return the 128-dimension face encoding for each face in the image.

        :param face_image: The image that contains one or more faces
        :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
        :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
        :param model: Optional - which model to use. "large" or "small" (default) which only returns 5 points but is faster.
        :return: A list of 128-dimensional face encodings (one for each face in the image)
        '''
        face_encodings = face_recognition.face_encodings(frame, face_boxes, model='small')

        # model for cloth encoding
        cloth_encoding_model = calc.get_model() # resnet

        fingerprints = dict()

        for i, face_box in enumerate(face_boxes):
            # crop face image
            upper_body_image, cloth_image = self.get_face_and_cloth_image(frame, face_box)
            # cloth preprocessing
            preprocessed_cloth_image = self.preprocess(cloth_image, (224, 224))
            # cloth_encodings
            cloth_encoding = calc.fingerprint(preprocessed_cloth_image, cloth_encoding_model)
            # normalize
            normalized_face_encoding = face_encodings[i] / np.linalg.norm(face_encodings[i])
            normalized_cloth_encoding = cloth_encoding / np.linalg.norm(cloth_encoding)
            # concat features [face | cloth]
            face_weight, cloth_weight = 1, 2
            encoding = np.concatenate((normalized_face_encoding*face_weight, normalized_cloth_encoding*cloth_weight), axis=0) # 128-d + 128-d
            # encoding = normalized_face_encoding
            # encoding = normalized_cloth_encoding
            # encoding = face_encodings[i]
            # encoding = cloth_encoding
            # filename
            filename = str_ms + str(i) + ".png"
            # save image
            # face = Face(str_ms + str(i) + ".png", upper_body_image, encoding)
            filepath = os.path.join(self.save_dir, filename)
            cv2.imwrite(filepath, upper_body_image)
            print('image saved path: ', filepath)
            # save fingerprint
            fingerprints[filepath] = encoding

        return fingerprints