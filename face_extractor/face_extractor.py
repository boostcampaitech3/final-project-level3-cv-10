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
import os.path as osp
import glob
import matplotlib.pyplot as plt
from imagecluster import FaceClassifier, calc, icio, postproc
from imagecluster import Person, Face, PersonDB
import random
import torch

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


    def extract_fingerprints(self):
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
            last_down_frame = cur_down_frame
            last_org_frame = frame
            
            if rgb_distance > transition_threshold and frame_idx - start_frame_idx > min_scene_frames:
                print("({}~{})".format(start_frame_idx, frame_idx), "| idx", frame_idx)
                
                start_org_frame = cv2.resize(start_org_frame, None, fx=0.8, fy=0.8)
                last_org_frame = cv2.resize(last_org_frame, None, fx=0.8, fy=0.8)
                
                frames.append(start_org_frame)
                frames.append(last_org_frame)
                
                cv2.imwrite("cluster_test/{}.png".format(start_frame_idx), start_org_frame)
                cv2.imwrite("cluster_test/{}.png".format(frame_idx - 1), last_org_frame)
                start_frame_idx = frame_idx
                start_down_frame = cur_down_frame
                start_org_frame = frame
                
            if len(frames) < self.frame_batch_size:
                frame_idx += 1
                continue
                
            print("Frames len: ", len(frames))
   
           
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
                    print("Face images: ", len(fingerprints))
                    
                frames = []
                
            if len(fingerprints) >= self.face_cnt:
                break
                
            frame_idx += 1

        self.src.release()
        total_end_time = time.time()
        print("Total Time Taken: {} seconds".format(total_end_time - total_start_time))
        print("Captured frames: ", frame_idx)

        return fingerprints
    
    def cluster_fingerprints(self, fingerprints):
        clusters = calc.cluster(fingerprints, sim=self.threshold, method='single', min_csize=3)
        postproc.make_links(clusters, osp.join(self.result_dir, 'imagecluster/clusters'))
        images = icio.read_images(self.result_dir, size=(224, 224))
        fig, ax = postproc.plot_clusters(clusters, images)
        fig.savefig(os.path.join(self.result_dir, 'imagecluster/_cluster.png'))
        postproc.plt.show()
        return clusters
        

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
        print("Process every {} secs ({} frames)".format(self.skip_seconds, self.skip_frames))
        print("-"*80)


    def summarize_results(self):
        print("-"*80)
        print("Saved directory: {}".format(self.save_dir))
        print("Access persons: pdb.persons (list)")
        print("Access a person's name: p.name")
        print("Access a person's average encoding: p.encoding")
        print("Access a person's faces: p.faces")
        for person in self.pdb.persons:
            print("[{}]: {} samples".format(person.name, len(person.faces)))
        print("-"*80)
