from .person_db import Person
from .person_db import Face
from .person_db import PersonDB
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

class FaceExtractor:
    def __init__(self, video_path, data_dir='data/', save_dir='result', sim_thresh=0.35, skip_seconds=1, use_clipped_video=False, clip_start=0, clip_end=60):
        '''
        :param video_path : input video absolute path
        :param sim_thresh : similarity threshold for comparing two faces
        :param skip_seconds : skip interval in seconds
        :use_clipped_video : whether the given video_path refers to the original(long) video or clipped(short) video.
                            if original, then automatically clip it to shorter video for faster procesing
        '''
        self.person_id = 0
        self.save_dir = save_dir
        self.data_dir = data_dir

        self.video_path = video_path
        if not use_clipped_video:
            self.clip_video(clip_start, clip_end) # save clipped video to data_dir

        print("video_path:", self.video_path)

        self.src = cv2.VideoCapture(self.video_path)
        self.sim_thresh = sim_thresh
        self.skip_seconds = skip_seconds
        self.skip_frames = int(round(self.src.get(5) * self.skip_seconds))

        self.src_info = {
            'frame_w': self.src.get(cv2.CAP_PROP_FRAME_WIDTH),
            'frame_h': self.src.get(cv2.CAP_PROP_FRAME_HEIGHT),
            'frame_rate': self.src.get(cv2.CAP_PROP_FPS),
            'num_frames': self.src.get(cv2.CAP_PROP_FRAME_COUNT),
            'num_seconds': self.src.get(cv2.CAP_PROP_FRAME_COUNT) / self.src.get(cv2.CAP_PROP_FPS)
        }

        self.predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
        self._print_src_info()
        self.pdb = PersonDB()


    def extract_faces(self):
        total_start_time = time.time()
        frame_cnt = 0

        while True:
            success, frame = self.src.read()
            if frame is None:
                break

            frame_cnt += 1
            if frame_cnt % self.skip_frames != 0:
                continue

            start_time = time.time()
            faces = self.detect_faces(frame)
            for face in faces:
                person = self.compare_with_known_persons(face, self.pdb.persons)
                if person:
                    continue

                person = self.compare_with_unknown_faces(face, self.pdb.unknown.faces)
                if person:
                    self.pdb.persons.append(person)

            elapsed_time = time.time() - start_time

            s = "\rframe " + str(frame_cnt)
            #  s += " @ time %.3f" % seconds
            s += " takes %.3f second" % elapsed_time
            s += ", %d new faces" % len(faces)
            s += " -> " + repr(self.pdb)
            print(s, end="    ")

        self.src.release()
        self.pdb.save_db(self.save_dir)
        self.pdb.print_persons()

        total_end_time = time.time()

        print("Total Time Taken: {} seconds".format(total_end_time - total_start_time))

        return self.pdb



    def get_face_image(self, frame, box):
        img_height, img_width = frame.shape[:2]
        (box_top, box_right, box_bottom, box_left) = box
        box_width = box_right - box_left
        box_height = box_bottom - box_top
        crop_top = max(box_top - box_height, 0)
        pad_top = -min(box_top - box_height, 0)
        crop_bottom = min(box_bottom + box_height, img_height - 1)
        pad_bottom = max(box_bottom + box_height - img_height, 0)
        crop_left = max(box_left - box_width, 0)
        pad_left = -min(box_left - box_width, 0)
        crop_right = min(box_right + box_width, img_width - 1)
        pad_right = max(box_right + box_width - img_width, 0)
        face_image = frame[crop_top:crop_bottom, crop_left:crop_right]
        if (pad_top == 0 and pad_bottom == 0):
            if (pad_left == 0 and pad_right == 0):
                return face_image
        padded = cv2.copyMakeBorder(face_image, pad_top, pad_bottom,
                                    pad_left, pad_right, cv2.BORDER_CONSTANT)
        return padded


    # return list of dlib.rectangle
    def locate_faces(self, frame):
        #start_time = time.time()
        rgb = frame[:, :, ::-1]
        boxes = face_recognition.face_locations(rgb)
        #elapsed_time = time.time() - start_time
        #print("locate_faces takes %.3f seconds" % elapsed_time)
        return boxes


    def detect_faces(self, frame):
        boxes = self.locate_faces(frame)
        if len(boxes) == 0:
            return []

        # faces found
        faces = []
        now = datetime.now()
        str_ms = now.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '-'

        for i, box in enumerate(boxes):
            # extract face image from frame
            face_image = self.get_face_image(frame, box)

            # get aligned image
            aligned_image = face_alignment_dlib.get_aligned_face(self.predictor, face_image)

            # compute the encoding
            height, width = aligned_image.shape[:2]
            x = int(width / 3)
            y = int(height / 3)
            box_of_face = (y, x*2, y*2, x)
            encoding = face_recognition.face_encodings(aligned_image,
                                                       [box_of_face])[0]

            face = Face(str_ms + str(i) + ".png", face_image, encoding)
            face.location = box
            # cv2.imwrite(str_ms + str(i) + ".r.png", aligned_image)
            faces.append(face)
        return faces


    def compare_with_known_persons(self, face, persons):
        if len(persons) == 0:
            return None

        # see if the face is a match for the faces of known person
        encodings = [person.encoding for person in persons]
        distances = face_recognition.face_distance(encodings, face.encoding)
        index = np.argmin(distances)
        min_value = distances[index]
        if min_value < self.sim_thresh:
            # face of known person
            persons[index].add_face(face)
            # re-calculate encoding
            persons[index].calculate_average_encoding()
            face.name = persons[index].name
            return persons[index]


    def compare_with_unknown_faces(self, face, unknown_faces):
        if len(unknown_faces) == 0:
            # this is the first face
            unknown_faces.append(face)
            face.name = "unknown"
            return

        encodings = [face.encoding for face in unknown_faces]
        distances = face_recognition.face_distance(encodings, face.encoding)
        index = np.argmin(distances)
        min_value = distances[index]
        if min_value < self.sim_thresh:
            # two faces are similar - create new person with two faces
            person = Person(person_id=self.person_id) #
            self.person_id += 1 #
            newly_known_face = unknown_faces.pop(index)
            person.add_face(newly_known_face)
            person.add_face(face)
            person.calculate_average_encoding()
            face.name = person.name
            newly_known_face.name = person.name
            return person
        else:
            # unknown face
            unknown_faces.append(face)
            face.name = "unknown"
            return None


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
        print("[Frame rate]: {}".format(int(self.src_info['frame_rate'])))
        print("[Total number of frames]: {}".format(int(self.src_info['num_frames'])))
        print("[Total number of seconds]: {}".format(int(self.src_info['num_seconds'])))
        print("[Similiarty Threshold]: {}".format(self.sim_thresh))
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
