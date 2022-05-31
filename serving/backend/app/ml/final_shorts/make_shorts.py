from moviepy.editor import *
import os

def make_shorts(final_highlights, total_length, id, target_person):
    print("Making Shorts....")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    FILE_DIR = os.path.join(BASE_DIR, 'files/')

    SHORTS_DIR = os.path.join(FILE_DIR, id, 'shorts')
    os.makedirs(SHORTS_DIR, exist_ok=True)
    

    VIDEO_DIR = os.path.join(FILE_DIR, id, "original.mp4")
    print(VIDEO_DIR)

    target_person_shorts = []
    for idx, (start, end, interest, during) in enumerate(final_highlights):
        print("Making Clips...")
        HIGHLIGHT_PATH = os.path.join(SHORTS_DIR, f"short_{target_person}_{idx}.mp4")
        clip = VideoFileClip(VIDEO_DIR).subclip(start,end).fx(vfx.fadein,1).fx(vfx.fadeout,1)
        clip.write_videofile(HIGHLIGHT_PATH)
        target_person_shorts.append([target_person, HIGHLIGHT_PATH, during, interest])

    return target_person_shorts