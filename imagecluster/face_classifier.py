#!/usr/bin/env python3

from .person_db import Person
from .person_db import Face
from .person_db import PersonDB
import face_recognition
import numpy as np
from datetime import datetime
import cv2
import os

import time
import torch
from torch import nn
import numpy as np

from PIL import Image
import matplotlib.pyplot as plt

from . import calc


class FaceClassifier():
    def __init__(self, threshold, ratio, save_dir):
        self.similarity_threshold = threshold
        self.ratio = ratio
        self.save_dir = save_dir

    def get_face_and_cloth_image(self, frame, boxes):
        '''
        param:
            frame: 프레임 이미지
            box: 좌표값 list [(top, right, bottom, left), ...]
        return:
            padded_faces: 얼굴 이미지 list [(numpy array), ...]
            padded_clothes: 옷 이미지 list [(numpy array), ...]
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
                # arr = np.asarray(img).astype(int)
                imgs.append(img)
            return imgs # arr
        except OSError as ex:
            print(f"skipping file...: {ex}")
            return None
        

    def detect_faces(self, frames, batch_size):
        # face locations
        # rgb_frames = [x[:, :, ::-1] for x in frames]
        batch_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0, batch_size=batch_size)
        frames = [frames[i] for i in range(len(frames)) if 2 <= len(batch_face_locations[i]) <= 4]
        batch_face_locations = [x for x in batch_face_locations if (2 <= len(x) <= 4)]

        if len(batch_face_locations) == 0:
            return None

        faces = []
        now = datetime.now()
        str_ms = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '-'

        cloth_encoding_model = calc.get_model() # resnet

        fingerprints = dict()
        face_encodings_batch = []
        upper_body_images_batch = []
        clothes_batch = []
        
        for frame_number_in_batch, face_locations in enumerate(batch_face_locations):
            face_encodings = []
            for face_location in face_locations:
                top, right, bottom, left = face_location
                resized_frame = cv2.resize(frames[frame_number_in_batch][top:bottom,left:right], dsize=(224,224))
                resized_encodings = face_recognition.face_encodings(resized_frame,[(0,223,223,0)], model='small')[0] # list 안에 인물 수만큼 numpy array
                face_encodings.append(resized_encodings)
            # crop face image
            upper_body_images, cloth_images = self.get_face_and_cloth_image(frames[frame_number_in_batch], face_locations) # list 형태로 반환
            # cloth preprocessing
            preprocessed_cloth_images = self.preprocess(cloth_images, (224,224))
            
            # save batch
            face_encodings_batch.extend(face_encodings)
            upper_body_images_batch.extend(upper_body_images)
            clothes_batch.extend(preprocessed_cloth_images)

        # cloth encodings
        # if len(clothes_batch) > 30:
        cloth_encodings = calc.fingerprint(clothes_batch, cloth_encoding_model, device = torch.device(device='cuda'))

        for i in range(len(face_encodings_batch)):
            # normalize
            normalized_face_encoding = face_encodings_batch[i] / np.linalg.norm(face_encodings_batch[i])
            normalized_cloth_encoding = cloth_encodings[i] / np.linalg.norm(cloth_encodings[i])
            # concat features [face | cloth]
            face_weight, cloth_weight = 1, 2
            encoding = np.concatenate((normalized_face_encoding*face_weight, normalized_cloth_encoding*cloth_weight), axis=0) # 128-d + 128-d

            filename = str_ms + str(i) + ".png"
            # save image
            # face = Face(str_ms + str(i) + ".png", upper_body_image, encoding)
            filepath = os.path.join(self.save_dir, filename)
            cv2.imwrite(filepath, upper_body_images_batch[i])
            print('image saved path: ', filepath)
            # save fingerprint
            fingerprints[filepath] = encoding

        return fingerprints