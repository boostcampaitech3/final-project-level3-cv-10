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

    def get_face_and_cloth_image(self, frame, boxes):
        '''
        param:
            frame: 프레임 이미지
            box: 좌표값 list [(top, right, bottom, left), (top, right, bottom, left), ..]
        return:
            padded_face: 얼굴 이미지 list [(numpy array), (numpy array), ...]
            padded_cloth: 옷 이미지 list  [(numpy array), (numpy array), ...]
        '''
        
        padded_faces = []
        padded_clothes = []
        
        img_height, img_width = frame.shape[:2]
        for box in boxes:
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
                    padded_faces.append(face_image)
                    padded_clothes.append(cloth_image)
                    continue
            padded_face = cv2.copyMakeBorder(face_image, pad_top, pad_bottom,
                                            pad_left, pad_right, cv2.BORDER_CONSTANT)
            padded_cloth = cv2.copyMakeBorder(cloth_image, pad_top, pad_bottom,
                                             pad_left, pad_right, cv2.BORDER_CONSTANT)
            
            padded_faces.append(padded_face)
            padded_clothes.append(padded_cloth)
        return padded_faces, padded_clothes

    def preprocess(self, images, size):
        try:
            imgs = []
            for image in images:
                img = Image.fromarray(image).convert('RGB').resize(size, resample=3)
                imgs.append(img)
            return imgs
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

    def detect_faces(self, frames, batch_size):
        # face locations
        batch_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0, batch_size = batch_size)
        # 사람이 2명 ~ 4명 사이일 때만 수행
        new_frames = []
        for i in range(len(frames)):
            if 2<=len(batch_face_locations[i])<=4:
                new_frames.append(frames[i])
        frames = new_frames
        batch_face_locations = [x for x in batch_face_locations if (2<=len(x)<=4)]
        if len(batch_face_locations) == 0:
            return None
        
        # model for cloth encoding
        cloth_encoding_model = calc_new.get_model() # resnet
        
        # faces found
        faces = []

        # face_encodings
        '''
        Given an image, return the 128-dimension face encoding for each face in the image.

        :param face_image: The image that contains one or more faces
        :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
        :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
        :param model: Optional - which model to use. "large" or "small" (default) which only returns 5 points but is faster.
        :return: A list of 128-dimensional face encodings (one for each face in the image)
        '''
        fingerprints = dict()
        
        for frame_number_in_batch, face_locations in enumerate(batch_face_locations):
            face_encodings = face_recognition.face_encodings(frames[frame_number_in_batch], face_locations, model='large') # list 안에 인물 수 만큼 numpy array
            # crop face image
            upper_body_images, cloth_images = self.get_face_and_cloth_image(frames[frame_number_in_batch], face_locations) # list 형태로 반환
            # cloth preprocessing
            preprocessed_cloth_images = self.preprocess(cloth_images, (224, 224))
            # cloth_encodings
            cloth_encodings = calc_new.fingerprint(preprocessed_cloth_images, cloth_encoding_model,device = torch.device(device='cuda'))
            
            now = datetime.now()
            str_ms = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '-'
            for i in range(len(face_encodings)):
                # normalize
                normalized_face_encoding = face_encodings[i] / np.linalg.norm(face_encodings[i])
                normalized_cloth_encoding = cloth_encodings[i] / np.linalg.norm(cloth_encodings[i])
                # concat features [face | cloth]
                encoding = np.concatenate((normalized_face_encoding, normalized_cloth_encoding), axis=0) # 128-d + 512-d
                # filename
                filename = str_ms + str(i) + ".png"
                # save image
                # face = Face(str_ms + str(i) + ".png", upper_body_image, encoding)
                filepath = os.path.join(self.save_dir, filename)
                cv2.imwrite(filepath, upper_body_images[i])
                print('image saved path: ', filepath)
                # save fingerprint
                fingerprints[filepath] = encoding


        return fingerprints