from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import cv2

app = FastAPI()

origins = [
    "http://34.64.208.21:30002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello Goodbye"}


@app.post("/upload/")
async def upload_video(video: UploadFile = File(...)):
    video_input = await video.read()
    print(video_input)
    # video_bytes = cv2.VideoCapture(video_input)
    # return video_bytes

# TODO: Video Upload 구현, Image Upload 구현
    # TODO: 비디오(Video_info) : Request
    
# TODO: upload_video(POST) : 영상을 업로드 합니다. => laught detection과 faceclustering을 진행한다.
# TODO: read_images(GET) : 생성된 이미지들을 보여줍니다.
# TODO: upload_image(POST) : 이미지를 업로드 합니다.(속도를 위해 경로를 설정해 줄 수도 있을 것 같다.)
# TODO: read_shorts(GET) : 생성된 하이라이트들을 보여줍니다.
