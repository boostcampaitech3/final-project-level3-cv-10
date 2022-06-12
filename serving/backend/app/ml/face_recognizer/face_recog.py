import dlib
import face_recognition
import torch
import cv2
import numpy as np
from PIL import Image
import sys
sys.path.append('../')
import ml.imagecluster.calc as calc

class FaceRecognizer:
    def __init__(self,video_path,target_encoding,threshold=0.63,feature_weight=[2,1],batch_size=16):
        self.video_path = video_path
        self.target_encoding = target_encoding
        self.target_count = len(target_encoding)
        self.threshold = threshold
        self.weight = feature_weight
        self.batch_size = batch_size
        
        self.src = cv2.VideoCapture(self.video_path)
        self.src_info = {
            'frame_w': self.src.get(cv2.CAP_PROP_FRAME_WIDTH),
            'frame_h': self.src.get(cv2.CAP_PROP_FRAME_HEIGHT),
            'fps': self.src.get(cv2.CAP_PROP_FPS),
            'num_frames': self.src.get(cv2.CAP_PROP_FRAME_COUNT),
            'num_seconds': self.src.get(cv2.CAP_PROP_FRAME_COUNT) / self.src.get(cv2.CAP_PROP_FPS)
        }
        
        
    def initialize_gpu(self):
        test = np.array(np.random.rand(10,10,3),dtype='uint8')
        face_recognition.face_locations(test,model='cnn')
        

    def get_face_and_cloth_image(self, frame, boxes):
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
        
    def recognize_faces(self):
        frames = []
        frames_real_time = []
        output_frame = [[] for _ in range(self.target_count)]
        frame_num = 0
        cloth_encoding_model = calc.get_model()
        self.target_encoding = [np.concatenate([encoding[:128]*self.weight[0],encoding[128:]/0.7*self.weight[1]]) for encoding in self.target_encoding]
        
        last_frame = None
        start_frame_num = 0
        min_scene_frames = 15
        timelines = []
        total_target_frames = 100
        down_scale_factor = 10
        transition_threshold = 100
        
        self.initialize_gpu()

        while self.src.isOpened():
            ret, frame = self.src.read()
            if not ret:
                break
            
            # scene detect
            cur_frame = frame[::down_scale_factor, ::down_scale_factor, :]

            if last_frame is None:
                last_frame = cur_frame
                start_original_frame = frame
                last_original_frame = frame
                start_frame_num = frame_num
                frame_num += 1
                continue

            num_pixels = cur_frame.shape[0] * cur_frame.shape[1]
            rgb_distance = np.abs(cur_frame - last_frame) / float(num_pixels)
            rgb_distance = rgb_distance.sum() / 3.0
            last_frame = cur_frame
            start_original_frame = frame
                
            if rgb_distance > transition_threshold and frame_num - start_frame_num > min_scene_frames:
                timelines.append((start_frame_num, frame_num - 1))
                start_frame_num = frame_num
                
                last_original_frame = last_original_frame[:, :, ::-1]
                height, width = last_original_frame.shape[:2]
                last_original_frame = last_original_frame[int(height*0.2):, int(width*0.2):int(width*0.8)]
                if height > 800:
                    last_original_frame = cv2.resize(last_original_frame, None, fx=0.6, fy=0.6)    
                frames.append(last_original_frame)
                frames_real_time.append(frame_num-1)

                start_original_frame = start_original_frame[:, :, ::-1]
                height, width = start_original_frame.shape[:2]
                start_original_frame = start_original_frame[int(height*0.2):, int(width*0.2):int(width*0.8)]
                if height > 800:
                    start_original_frame = cv2.resize(start_original_frame, None, fx=0.6, fy=0.6)    
                frames.append(start_original_frame)
                frames_real_time.append(frame_num)

            # BATCH_SIZE에 도달하면 recognition수행
            if len(frames) == self.batch_size:
                batch_of_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0)
                for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
                    face_encodings = []
                    for face_location in face_locations:
                        top, right, bottom, left = face_location
                        resized_frame = cv2.resize(frames[frame_number_in_batch][top:bottom,left:right], dsize=(224,224))
                        resized_encodings = face_recognition.face_encodings(resized_frame,[(0,223,223,0)], model='small')[0] # list 안에 인물 수만큼 numpy array
                        face_encodings.append(resized_encodings)
                    if len(face_locations) > 0:
                        upper_body_images, cloth_images = self.get_face_and_cloth_image(frames[frame_number_in_batch], face_locations)
                        preprocessed_cloth_images = self.preprocess(cloth_images, (224, 224))
                        cloth_encodings = calc.fingerprint(preprocessed_cloth_images, cloth_encoding_model,device = torch.device(device='cuda'))
                        for i in range(len(face_encodings)):
                            normalized_face_encoding = face_encodings[i] / np.linalg.norm(face_encodings[i])
                            normalized_cloth_encoding = cloth_encodings[i] / np.linalg.norm(cloth_encodings[i])
                            encoding = np.concatenate((normalized_face_encoding*self.weight[0], normalized_cloth_encoding*self.weight[1]), axis=0)
                            match = face_recognition.compare_faces(self.target_encoding, encoding, tolerance=self.threshold)
                            for i in range(len(match)):
                                if match[i]:
                                    output_frame[i].append(frames_real_time[frame_number_in_batch])

                frames = []
                frames_real_time = []
                
            last_original_frame = frame
            frame_num += 1 

        # 마지막 batch 처리
        if len(frames) > 0:
            batch_of_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0)
            for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
                face_encodings = face_recognition.face_encodings(frames[frame_number_in_batch], face_locations)
                if len(face_locations) > 0:
                    upper_body_images, cloth_images = self.get_face_and_cloth_image(frames[frame_number_in_batch], face_locations)
                    preprocessed_cloth_images = self.preprocess(cloth_images, (224, 224))
                    cloth_encodings = calc.fingerprint(preprocessed_cloth_images, cloth_encoding_model,device = torch.device(device='cuda'))
                    for i in range(len(face_encodings)):
                        normalized_face_encoding = face_encodings[i] / np.linalg.norm(face_encodings[i])
                        normalized_cloth_encoding = cloth_encodings[i] / np.linalg.norm(cloth_encodings[i])
                        encoding = np.concatenate((normalized_face_encoding*self.weight[0], normalized_cloth_encoding*self.weight[1]), axis=0)
                        match = face_recognition.compare_faces(self.target_encoding, encoding, tolerance=self.threshold)
                        for i in range(len(match)):
                            if match[i]:
                                output_frame[i].append(frames_real_time[frame_number_in_batch])
                            
        self.src.release()
        
        return timelines, output_frame
    
    
    def make_people_timeline(self,scene_frame,people_frame, target_people):
        fps = self.src_info['fps']
        people_timeline = {}
        for idx, person_frame in enumerate(people_frame):
            if len(person_frame)==0:
                people_timeline[target_people[idx]] = []
                continue
            person_timeline=[]
            scene_index = 0
            for frame in person_frame:
                for i in range(scene_index, len(scene_frame)):
                    start, end = scene_frame[i]
                    if start<=frame<=end:
                        person_timeline.append((round(start/fps,2), round(end/fps,2)))
                        scene_index = i+1
                        break
            people_timeline[target_people[idx]] = person_timeline

        return people_timeline