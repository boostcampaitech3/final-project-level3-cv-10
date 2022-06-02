import face_recognition
import face_recognition_models
import numpy as np
from datetime import datetime
import cv2
import dlib
from . import face_alignment_dlib
import time
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os.path as osp
import sys
import os
import glob
import matplotlib.pyplot as plt
from imagecluster import FaceClassifier, calc, icio, postproc
from imagecluster import Person, Face, PersonDB
import random
import torch
import matplotlib.pyplot as plt

class FaceExtractor:
    def __init__(self, video_path, data_dir='data/', result_dir='result', threshold=0.48, skip_seconds=3, use_clipped_video=True, clip_start=0, clip_end=60,
                frame_batch_size=16, stop=300, skip=0, face_cnt=250, capture_cnt=60, ratio=1.0): # face_cnt=150 원래
        '''
        :param video_path : input video absolute path
        :param sim_thresh : similarity threshold for comparing two faces
        :param skip_seconds : skip interval in seconds
        :use_clipped_video : whether the given video_path refers to the original(long) video or clipped(short) video.
                            if original, then automatically clip it to shorter video for faster procesing
        '''
        # Path
        self.video_path = video_path
        self.data_dir = data_dir
        self.result_dir = result_dir
        
        # Clustering configs
        self.frame_batch_size = frame_batch_size
        self.stop = stop
        self.skip = skip
        self.face_cnt = face_cnt
        self.capture_cnt = capture_cnt
        self.ratio = ratio
        self.threshold = threshold
        
        self.merged_cluster_dir = None
        self.fingerprints = None
        self.clusters = None
        self.final_dict = None
        self.time_record = dict()
        
        if not osp.isdir(self.result_dir):
            os.makedirs(self.result_dir)
        
        # Clip
        if not use_clipped_video:
            self.clip_video(clip_start, clip_end) # save clipped video to data_dir

        # Import video
        self.src = cv2.VideoCapture(self.video_path)
        self.skip_seconds = skip_seconds
        self.skip_frames = int(round(self.src.get(5) * self.skip_seconds))

        self.src_info = {
            'frame_w': self.src.get(cv2.CAP_PROP_FRAME_WIDTH),
            'frame_h': self.src.get(cv2.CAP_PROP_FRAME_HEIGHT),
            'fps': self.src.get(cv2.CAP_PROP_FPS),
            'num_frames': self.src.get(cv2.CAP_PROP_FRAME_COUNT),
            'num_seconds': self.src.get(cv2.CAP_PROP_FRAME_COUNT) / self.src.get(cv2.CAP_PROP_FPS)
        }
        
        # Face Classifier
        self.fc = FaceClassifier(self.threshold, self.ratio, self.result_dir)
        
        self._print_src_info()
        
        self.seed_everything(79)
        
        TARGET_IMG_PATH = "/opt/ml/input/final-project-level3-cv-10/data/img1.png"
        self.check_use_gpu(TARGET_IMG_PATH) 

    
    def cluster_video(self):
        fingerprints = self.extract_fingerprints()
        clusters = self.cluster_fingerprints(fingerprints)
        self.merge_clusters(clusters, fingerprints)
        final_dict = self.get_final_dict()
        
        return final_dict
    
    
    def extract_fingerprints(self):
        print(">>> Extracting fingerprints...")
        total_start_time = time.time()
        
        fingerprints = dict()
        frames = []
        frame_idx = 0
        cnt = 0
        
        # Scene Detection
        last_down_frame = None
        last_org_frame = None
        
        start_frame_idx = 0
        start_down_frame = None
        start_org_frame = None
        min_scene_frames = 15
        timelines = []
        down_scale_factor = 8
        transition_threshold = 100

        while True:
            success, frame = self.src.read()
            if frame is None:
                break
            
            ###### Preprocessing ######
            seconds = int(round(frame_idx / self.src_info['fps'], 3))
            
            # Maximum seconds to explore
            if seconds > self.stop > 0:
                break
            
            # Skip first n seconds
            if seconds < self.skip:
                continue
                
            ####### Scene Detection Algorithm ######
            cur_down_frame = frame[::down_scale_factor, ::down_scale_factor, :]
            
            if last_down_frame is None:
                last_down_frame = cur_down_frame
                last_org_frame = frame
                start_frame_idx = frame_idx
                start_down_frame = cur_down_frame
                start_org_frame = frame
                frame_idx += 1
                continue
                
            num_pixels = cur_down_frame.shape[0] * cur_down_frame.shape[1]
            rgb_distance = np.abs(cur_down_frame - last_down_frame) / float(num_pixels)
            rgb_distance = rgb_distance.sum() / 3.0
            
            if rgb_distance > transition_threshold and frame_idx - start_frame_idx > min_scene_frames:
                # print("({}~{})".format(start_frame_idx, frame_idx-1))
                
                start_org_frame = cv2.resize(start_org_frame, None, fx=0.8, fy=0.8)
                last_org_frame = cv2.resize(last_org_frame, None, fx=0.8, fy=0.8)
                
                frames.append(start_org_frame)
                frames.append(last_org_frame)
                
                # cv2.imwrite("scene_detection_imgs/{}.png".format(start_frame_idx), start_org_frame)
                # cv2.imwrite("scene_detection_imgs/{}.png".format(frame_idx - 1), last_org_frame)
                
                start_frame_idx = frame_idx
                start_down_frame = cur_down_frame
                start_org_frame = frame
            
            last_down_frame = cur_down_frame
            last_org_frame = frame
            
            if len(frames) < self.frame_batch_size:
                frame_idx += 1
                continue
           
            ##### Face Detection #####
            # # Explore every n frame
            # if frame_cnt % self.skip_frames == 0:
            #     if frame.shape[0] > 1000:
            #         frame = cv2.resize(frame, None, fx=0.6, fy=0.6)
            #     frames.append(frame)
                
            if len(frames) == self.frame_batch_size:
                frame_fingerprints = self.fc.detect_faces(frames, self.frame_batch_size)
                if frame_fingerprints:
                    fingerprints.update(frame_fingerprints)
                    # print("Face images: ", len(fingerprints))
                    
                frames = []
                
            if len(fingerprints) >= self.face_cnt:
                break
                
            frame_idx += 1

        self.src.release()
        total_end_time = time.time()
        self.time_record['Face Extraction'] = total_end_time - total_start_time
        # print("Captured frames: ", frame_idx)
        self.fingerprints = fingerprints
        
        return fingerprints
    
    def cluster_fingerprints(self, fingerprints):
        start_time = time.time()
        print(">>> Clustering fingerprints...")
        clusters = calc.cluster(fingerprints, sim=self.threshold, method='single', min_csize=3)
        postproc.make_links(clusters, osp.join(self.result_dir, 'imagecluster/clusters'))
        # images = icio.read_images(self.result_dir, size=(224, 224))
        # fig, ax = postproc.plot_clusters(clusters, images)
        # fig.savefig(os.path.join(self.result_dir, 'imagecluster/_cluster.png'))
        # postproc.plt.show()
        self.clusters = clusters
        
        end_time = time.time()
        self.time_record['Clustering Fingerprints'] = end_time - start_time
        
        return clusters
    
    
    def merge_clusters(self, cluster_dict, fingerprints, iteration=1, FACE_THRESHOLD_HARD=0.18, CLOTH_THRESHOLD_HARD=0.12, FACE_THRESHOLD_SOFT=0.19, CLOTH_THRESHOLD_SOFT=0.15) -> dict:
        '''
        parameters:
            clusters: calc.cluster() 의 return 값 (dict / key=cluster_size(int), value=clusters(2d-array))
            fingerprints: feature vector dictionary (key=filepath, value=feature vector)
            iteration: merge 반복 횟수
            FACE_THRESHOLD_HARD
            CLOTH_THRESHOLD_HARD
            FACE_THRESHOLD_SOFT
            CLOTH_THRESHOLD_SOFT
        return:
            merged_clusters: calc.cluster() 의 return 값과 동일한 형태 (dict / key=cluster_size(int), value=clusters(2d-array))
        '''

        print(">>> Merging clusters...")
        start_time = time.time()
        
        for _ in range(iteration):
            cluster_list = sorted([[key, value] for key, value in cluster_dict.items()], key=lambda x:x[0], reverse=True)
            cluster_fingerprints = [] # [(face, cloth), ...]
            cluster_cnt = 0

            for cluster_with_num in cluster_list:
                num, clusters = cluster_with_num
                for idx, cluster in enumerate(clusters):
                    cluster_face_fingerprint = np.zeros((128,))
                    cluster_cloth_fingerprint = np.zeros((128,))
                    i = 0
                    for person in cluster:
                        encoding = fingerprints[person]
                        face, cloth = encoding[:128], encoding[128:]
                        cluster_face_fingerprint += face
                        cluster_cloth_fingerprint += cloth
                        i += 1
                    assert i > 0, 'cluster is empty!'
                    cluster_face_fingerprint /= i
                    cluster_cloth_fingerprint /= i

                    cluster_fingerprints.append([(num, idx), (cluster_face_fingerprint, cluster_cloth_fingerprint)])
                    cluster_cnt += 1

            merged = []
            merged_clusters = dict()

            for i in range(cluster_cnt):
                if cluster_fingerprints[i][0] in merged:
                    continue
                big_num, big_idx = cluster_fingerprints[i][0]
                person_list = cluster_dict[big_num][big_idx]
                merged_num = big_num
                for j in range(i+1, cluster_cnt):
                    cluster_face_norm = round(np.linalg.norm(cluster_fingerprints[i][1][0] - cluster_fingerprints[j][1][0]),3)
                    cluster_cloth_norm = round(np.linalg.norm(cluster_fingerprints[i][1][1] - cluster_fingerprints[j][1][1]),3)
                    if cluster_face_norm < FACE_THRESHOLD_HARD or cluster_cloth_norm < CLOTH_THRESHOLD_HARD or \
                        (cluster_face_norm < FACE_THRESHOLD_SOFT and cluster_cloth_norm < CLOTH_THRESHOLD_SOFT):
                        small_num, small_idx = cluster_fingerprints[j][0]
                        merged_num += small_num
                        person_list += cluster_dict[small_num][small_idx]
                        merged.append(cluster_fingerprints[j][0])

                merged_clusters[merged_num] = merged_clusters.get(merged_num, [])
                merged_clusters[merged_num].append(person_list)

            cluster_dict = merged_clusters
        self.merged_cluster_dir = os.path.join(self.result_dir, 'imagecluster/merged_clusters')
        postproc.make_links(merged_clusters, self.merged_cluster_dir)

        end_time = time.time()
        self.time_record['Merging Clusters'] = end_time - start_time
        return merged_clusters
    
    def get_final_dict(self):
        print(">>> Calculating average encoding and representative encoding...")
        start_time = time.time()
        
        final_selections = dict()
        cnt = 0

        for sup_cluster in os.listdir(self.merged_cluster_dir):
            for cluster_folder in os.listdir(osp.join(self.merged_cluster_dir, sup_cluster)):
                
                # cluster folder
                cluster_dir = osp.join(self.merged_cluster_dir, sup_cluster, cluster_folder)

                # representative cluster & result path
                repr_cluster_img_path, avg_encoding = self.pick_one(cluster_dir)
                repr_result_img_path = osp.join(self.result_dir, repr_cluster_img_path.split('/')[-1])

                # repr_img, repr_encoding, avg_encoding
                repr_img = cv2.imread(repr_result_img_path)
                repr_img = cv2.cvtColor(repr_img, cv2.COLOR_BGR2RGB)
                repr_encoding = self.fingerprints[repr_result_img_path]

                final_selections[f'person_{cnt}'] = {
                    'repr_img_path': repr_result_img_path,
                    'repr_img_array': repr_img,
                    'repr_encoding': repr_encoding,
                    'avg_encoding': avg_encoding
                }

                cnt += 1
                
        end_time = time.time()
        self.time_record['Average Encoding & Pick Representative'] = end_time - start_time
        
        self.final_dict = final_selections
        return final_selections

    def detect_blur_fft(self, image, size=60):
        # grab the dimensions of the image and use the dimensions to
        # derive the center (x, y)-coordinates
        (h, w) = image.shape
        (cX, cY) = (int(w / 2.0), int(h / 2.0))
        fft = np.fft.fft2(image)
        fftShift = np.fft.fftshift(fft)
        fftShift[cY - size:cY + size, cX - size:cX + size] = 0
        fftShift = np.fft.ifftshift(fftShift)
        recon = np.fft.ifft2(fftShift)
        # compute the magnitude spectrum of the reconstructed image,
        # then compute the mean of the magnitude values

        magnitude = 20 * np.log(np.abs(recon))
        mean = np.mean(magnitude)
        # the image will be considered "blurry" if the mean value of the
        # magnitudes is less than the threshold value
        return (mean)

    def pick_one(self, FILE_PATH):
        mean = []
        avg_encoding = np.zeros(256)
        img_cnt = 0

        for i, imagePath in enumerate(os.listdir(FILE_PATH)):
            if not imagePath.endswith('.png') and not imagePath.endswith('.jpg'):
                continue

            # Calculate Average Encoding
            avg_encoding += self.fingerprints[osp.join(self.result_dir, imagePath)]

            # Pick a representative
            orig = cv2.imread(os.path.join(FILE_PATH,imagePath))
            # orig = imutils.resize(orig, width=500)
            gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)

            # apply our blur detector using the FFT
            mean.append( [imagePath, round(self.detect_blur_fft(gray, size=60),3 )])
            img_cnt += 1

        avg_encoding /= float(img_cnt)

        #sort in descending order by sharpness 
        mean = sorted(mean, key = lambda x: x[1], reverse = True)
        #return FILE_PATH + FILE_NAME
        return os.path.join(FILE_PATH,mean[0][0]), avg_encoding


    def clip_video(self, start, end):
        print("-"*80)
        print("Start clipping video from {} to {} seconds...".format(start, end))
        video_name = self.video_path.split('/')[-1]
        split_name = video_name.split('.')
        new_video_name = split_name[0] + "_{}-{}s".format(start, end) + '.' + split_name[1]
        target_path = osp.join(self.data_dir, new_video_name)
        ffmpeg_extract_subclip(self.video_path, start, end, targetname=target_path)
        self.video_path = target_path
        print("-"*80)


    def _print_src_info(self):
        print("-"*80)
        print("[Source Video File]: {}".format(self.video_path))
        print("[Frame resolution H x W]: ({} x {})".format(self.src_info['frame_h'], self.src_info['frame_w']))
        print("[FPS]: {}".format(int(self.src_info['fps'])))
        print("[Total number of frames]: {}".format(int(self.src_info['num_frames'])))
        print("[Total number of seconds]: {}".format(int(self.src_info['num_seconds'])))
        print("[Similiarty Threshold]: {}".format(self.threshold))
        print("[Number of target faces for clustering]: {}".format(self.face_cnt))
        print("Process every {} secs ({} frames)".format(self.skip_seconds, self.skip_frames))
        print("-"*80)


    def summarize_results(self):
        print("-"*32, "Result Summary", "-"*32)
        total_time = 0.
        for key, val in self.time_record.items():
            print("[{}]: {} seconds".format(key, round(val, 3)))
            total_time += val
        print("[Total time]: {} seconds".format(round(total_time, 3)))
        print("Total number of detected persons: {}".format(len(self.final_dict)))
        print("-"*80)
        
        
    def seed_everything(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = str(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)  # type: ignore
        torch.backends.cudnn.deterministic = True  # type: ignore
        torch.backends.cudnn.benchmark = False  # type: ignore
        
    def check_use_gpu(self, TARGET_IMG_PATH):
        image = face_recognition.load_image_file(TARGET_IMG_PATH)
        face_locations = face_recognition.face_locations(image,model='cnn')
        if len(face_locations) > 0:
            print('Using GPU')
        else:
            print('***Not using GPU***')
            
    
    def plot_clusters(self):
        num_persons = len(self.final_dict)
        h, w = num_persons, 1
        fig = plt.figure(figsize=(30, 70))

        idx = 0
        for person_id, info in self.final_dict.items():
            img = info['repr_img_array']
            fig.add_subplot(h, w, idx+1)
            plt.imshow(img)
            plt.axis('off')
            plt.title(person_id, color='red', fontsize=20)
            idx += 1


