import face_recognition
import cv2

def check_use_gpu(IMG):
    image = face_recognition.load_image_file(IMG)
    face_locations = face_recognition.face_locations(image, model='cnn')
    if len(face_locations) > 0:
        print('Using GPU')
    else:
        print('***Not using GPU***')

def make_face_timeline(VIDEO, IMG) -> list:
    ##### Set parameters #####
    # 몇 frame 마다 저장할 것인지(fps=대략 30)
    CHECK_FRAME = 16

    # batch 처리를 위한 batch size
    BATCH_SIZE = 16

    ##### Load video & face #####
    input_movie = cv2.VideoCapture(VIDEO)
    video_fps = input_movie.get(cv2.CAP_PROP_FPS)
    video_length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
    print(video_length)

    target_image = face_recognition.load_image_file(IMG)
    target_face_encoding = face_recognition.face_encodings(target_image)[0]

    check_use_gpu(IMG)

    known_faces = [target_face_encoding]

    ##### Inference #####
    frames = []
    frames_real_time = []
    output_frame = []
    frame_count = 0

    # while frame_count < 1000:
    while input_movie.isOpened():
        ret, frame = input_movie.read()
        if not ret:
            break

        # BGR -> RGB
        frame = frame[:, :, ::-1]

        # crop
        cropped = frame[int(frame.shape[0] * 0.2):int(frame.shape[0] * 0.8),
                  int(frame.shape[1] * 0.2):int(frame.shape[1] * 0.8)]
        frame = cropped

        # CHECK_FRAME 마다 frame을 batch에 저장
        if frame_count % CHECK_FRAME == 0:
            frames.append(frame)
            frames_real_time.append(frame_count)

        # BATCH_SIZE에 도달하면 recognition수행
        if len(frames) == BATCH_SIZE:
            batch_of_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0)
            for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
                face_encodings = face_recognition.face_encodings(frames[frame_number_in_batch], face_locations)
                for face_encoding in face_encodings:
                    match = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.50)
                    if match[0]:
                        output_frame.append(frames_real_time[frame_number_in_batch])

            frames = []
            frames_real_time = []

        frame_count += 1

        if frame_count % 3000 == 0:
            print("Writing frame {} / {}".format(frame_count, video_length))

    # 마지막 batch 처리
    if len(frames) > 0:
        batch_of_face_locations = face_recognition.batch_face_locations(frames, number_of_times_to_upsample=0)
        for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
            face_encodings = face_recognition.face_encodings(frames[frame_number_in_batch], face_locations)

            for face_encoding in face_encodings:
                match = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.50)
                if match[0]:
                    output_frame.append(frames_real_time[frame_number_in_batch])

    # All done!
    input_movie.release()
    cv2.destroyAllWindows()
    print(output_frame)

    timeline = make_person_timeline(output_frame, video_fps)
    return timeline


##### Make Timeline #####
# 타겟 인물이 등장하는 frame을 timeline으로 변환
def make_person_timeline(frames, fps):
    if len(frames) == 0:
        return None
    timeline = []
    start = frames[0]
    end = frames[0]
    for f in frames:
        if f - end > 33:
            timeline.append((round((start - 8) / fps, 2), round((end + 8) / fps, 2)))
            start, end = f, f
        else:
            end = f
    timeline.append((round((start - 8) / fps, 2), round(end / fps, 2)))
    return timeline