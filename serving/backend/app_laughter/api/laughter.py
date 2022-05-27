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


class VideoTimeline(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    file_name: str
    laughter_timeline: Optional[List[Tuple]]
    created_at : datetime = Field(default_factory=datetime.now)
    

@router.post("/timeline-laughter", description="비디오를 업로드하고 laughter detection을 수행합니다.")
async def get_laughter_timeline(file: UploadFile = File(...)):
    # download the uploaded video
    new_video_timeline = VideoTimeline(file_name=file.filename)
    os.makedirs(os.path.join(FILE_DIR, str(new_video_timeline.id)))
    server_path = os.path.join(FILE_DIR, str(new_video_timeline.id), ('original' + os.path.splitext(file.filename)[1]))
    with open(server_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # execute laughter detection    
    wav_path = os.path.join(FILE_DIR, str(new_video_timeline.id), 'for_laughter_detection')
    ml_path = os.path.join(BASE_DIR, 'ml')
    laughter_timeline = LaughterDetection(server_path, wav_path, ml_path)
    new_video_timeline.laughter_timeline = laughter_timeline

    # remove folder (laughter detection 서버에서는 일회성이므로)
    shutil.rmtree(os.path.join(FILE_DIR, str(new_video_timeline.id)))

    # TODO: timeline이 없을 때의 처리 추가 필요!

    return new_video_timeline


# TODO: /timeline-laughter (laughter detection을 통해 웃음 구간의 timeline 추출하기)
