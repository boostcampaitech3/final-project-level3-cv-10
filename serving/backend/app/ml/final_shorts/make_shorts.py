from moviepy.editor import *

from google.cloud import storage
storage_client = storage.Client()
bucket_name = 'snowman-bucket'
bucket = storage_client.bucket(bucket_name)

import os

def make_shorts(final_highlights, total_length, id, target_person):
    print("Making Shorts....")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    FILE_DIR = os.path.join(BASE_DIR, 'files/')

    SHORTS_DIR = os.path.join(FILE_DIR, id, 'shorts')
    SHORTS_STORAGE_DIR = os.path.join(id, 'shorts')
    os.makedirs(SHORTS_DIR, exist_ok=True)
    

    VIDEO_DIR = os.path.join(FILE_DIR, id, "original.mp4")
    print(VIDEO_DIR)

    # CURRENT_DIR = os.getcwd()

    # in_file = ffmpeg.input(VIDEO_DIR)

    target_person_shorts = []
    for idx, (start, end, interest, during) in enumerate(final_highlights):
        print("Making Clips...")
        HIGHLIGHT_PATH = os.path.join(SHORTS_DIR, f"short_{target_person}_{idx}.mp4")

        # save to gcs
        HIGHLIGHT_STORAGE_DIR = os.path.join(SHORTS_STORAGE_DIR, f"short_{target_person}_{idx}.mp4")
        blob = bucket.blob(HIGHLIGHT_STORAGE_DIR)
        
        trim_and_fade(VIDEO_DIR, start, end, HIGHLIGHT_PATH)

        # clip = VideoFileClip(VIDEO_DIR).subclip(start,end).fx(vfx.fadein,1).fx(vfx.fadeout,1)        
        
        # os.chdir(SHORTS_DIR) # for saving [video-name]TEMP_MPY_wvf_snd.mp3 file in files/[uuid]/shorts
        # clip.write_videofile(HIGHLIGHT_PATH)
        # os.chdir(CURRENT_DIR) # come back to original directory

        blob.upload_from_filename(HIGHLIGHT_PATH)

        target_person_shorts.append([target_person, HIGHLIGHT_STORAGE_DIR, during, interest])

    return target_person_shorts


def trim_and_fade(original_path, start, end, save_path):
    os.system(f'ffmpeg -i {original_path} -ss {start} -to {end} -filter_complex \
        "fade=in:st={start}:d=1, fade=out:st={end-1}:d=1; \
        afade=in:st={start}:d=1, afade=out:st={end-1}:d=1" \
        -c:v libx264 -c:a aac {save_path}')
