import dlib
import face_recognition
import face_recognition_models
import cv2

class FaceRecognizer:
    def __init__(self,video_path,target_path,model_cfg):
        self.video_path = video_path
        self.target_path = target_path
        self.target_count = len(self.target_path)
        self.model_cfg = model_cfg
        
        self.src = cv2.VideoCapture(self.video_path)
        self.src_info = {
            'frame_w': self.src.get(cv2.CAP_PROP_FRAME_WIDTH),
            'frame_h': self.src.get(cv2.CAP_PROP_FRAME_HEIGHT),
            'fps': self.src.get(cv2.CAP_PROP_FPS),
            'num_frames': self.src.get(cv2.CAP_PROP_FRAME_COUNT),
            'num_seconds': self.src.get(cv2.CAP_PROP_FRAME_COUNT) / self.src.get(cv2.CAP_PROP_FPS)
        }
        
        
    def recognize_faces(self):
        # load target images
        target_image = [face_recognition.load_image_file(x) for x in self.target_path]
        target_loc = [face_recognition.face_locations(x, model="cnn") for x in target_image]
        target_face_encoding = [face_recognition.face_encodings(img,loc)[0] for img,loc in zip(target_image,target_loc)]
        known_faces = target_face_encoding
        
        frames = []
        frames_real_time = []
        output_frame = [[] for _ in range(self.target_count)]
        frame_count = 0

        while self.src.isOpened():
            ret, frame = self.src.read()
            if not ret:
                break

            # BGR->RGB & Crop
            frame = frame[:, :, ::-1]
            cropped = frame[int(frame.shape[0]*0.2):int(frame.shape[0]*0.8), int(frame.shape[1]*0.2):int(frame.shape[1]*0.8)]
            frame = cropped

            # CHECK_FRAME 마다 frame을 batch에 저장
            if frame_count % self.model_cfg['check_frame'] == 0:
                frames.append(frame)
                frames_real_time.append(frame_count)

            # BATCH_SIZE에 도달하면 recognition수행
            if len(frames) == self.model_cfg['batch_size']:
                batch_of_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0)
                for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
                    face_encodings = face_recognition.face_encodings(frames[frame_number_in_batch], face_locations)
                    for face_encoding in face_encodings:
                        match = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.40)
                        for i in range(len(match)):
                            if match[i]:
                                output_frame[i].append(frames_real_time[frame_number_in_batch])

                frames = []
                frames_real_time = []

            frame_count += 1 

        # 마지막 batch 처리
        if len(frames) > 0:
            batch_of_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0)
            for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
                face_encodings = face_recognition.face_encodings(frames[frame_number_in_batch], face_locations)

                for face_encoding in face_encodings:
                    match = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.40)
                    for i in range(len(match)):
                        if match[i]:
                            output_frame[i].append(frames_real_time[frame_number_in_batch])
                            
        self.src.release()
        
        return output_frame
    
    
    def make_people_timeline(self,frames):
        fps = self.src_info['fps']
        # people_timeline = []
        for frame in frames:
            person_timeline=[]
            if len(frame)==0:
                # people_timeline.append([])
                person_timeline.append([])
                continue
            # person_timeline=[]
            start=frame[0]
            end=frame[0]
            for f in frame:
                if f-end>33:
                    person_timeline.append((round((start-8)/fps,2),round((end+8)/fps,2)))
                    start,end=f,f
                else:
                    end = f
            person_timeline.append((round((start-8)/fps,2),round(end/fps,2)))
            # people_timeline.append(person_timeline)
        # return people_timeline
        return person_timeline