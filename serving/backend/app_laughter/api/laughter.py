from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException

import os
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
import shutil
from typing import List, Tuple, Optional

from ml.laughter_detection import LaughterDetection


router = APIRouter(tags=["timeline"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'files/')
ML_DIR = os.path.join(BASE_DIR, 'ml/')


class Video(BaseModel):
    id_laughter: UUID = Field(default_factory=uuid4)
    file_name: str
    created_at : datetime = Field(default_factory=datetime.now)


@router.post("/upload-video", description="비디오를 업로드합니다.")
async def create_video_file(file: UploadFile = File(...)):
    # download the uploaded video
    new_video = Video(file_name=file.filename)
    os.makedirs(os.path.join(FILE_DIR, str(new_video.id_laughter)))
    server_path = os.path.join(FILE_DIR, str(new_video.id_laughter), ('original' + os.path.splitext(file.filename)[1]))
    with open(server_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return new_video


class VideoTimeline(BaseModel):
    id: UUID
    # file_name: str
    laugh: Optional[List[Tuple]]
    # created_at : datetime
    

@router.post("/timeline-laughter", description="laughter detection을 수행하여 laughter timeline을 추출합니다.")
async def get_timeline_laughter(info: dict):
    new_video_timeline = VideoTimeline(id=info['id'])
    server_path = os.path.join(FILE_DIR, str(new_video_timeline.id))

    # execute laughter detection    
    wav_path = os.path.join(server_path, 'for_laughter_detection')
    video_path = os.path.join(server_path, os.listdir(server_path)[0])

    laughter_timeline = LaughterDetection(video_path, wav_path, ML_DIR)
    new_video_timeline.laugh = laughter_timeline

    # remove folder (laughter detection 서버에서는 일회성이므로)
    shutil.rmtree(os.path.join(FILE_DIR, str(new_video_timeline.id)))
    return new_video_timeline


# TODO: /laughter-detection (기존의 /upload-video와 /timeline-laughter 통합)

@router.post("/laughter-detection", description="laughter timeline을 추출하는 전과정을 수행합니다.")
async def laughter_detection(file: UploadFile = File(...)):
    # download the uploaded video
    new_video = Video(file_name=file.filename)
    os.makedirs(os.path.join(FILE_DIR, str(new_video.id_laughter)))
    video_path = os.path.join(FILE_DIR, str(new_video.id_laughter), ('original' + os.path.splitext(file.filename)[1]))
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # extract laughter timeline
    new_video_timeline = VideoTimeline(id=new_video.id_laughter)

    # execute laughter detection    
    wav_path = os.path.join(FILE_DIR, str(new_video.id_laughter), 'for_laughter_detection')

    laughter_timeline = LaughterDetection(video_path, wav_path, ML_DIR)
    new_video_timeline.laugh = laughter_timeline

    # remove folder (laughter detection 서버에서는 일회성이므로)
    shutil.rmtree(os.path.join(FILE_DIR, str(new_video_timeline.id)))
    return new_video_timeline
