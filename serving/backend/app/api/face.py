from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List
from PIL import Image
import base64
import io

from ml.face_functions import FaceRecognition



router = APIRouter(tags=["timeline"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'files/')


class People(BaseModel):
    id: UUID 
    people_img: Dict[str, bytes]
    file_name: str
    message: Optional[str]
    # created_at : datetime = Field(default_factory=datetime.now)

class ItemValue(BaseModel):
    id: str
    person: str


def from_img_to_bytes(img):
    """
    pillow image 객체를 bytes로 변환
    """
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format=img.format)
    imgByteArr = imgByteArr.getvalue()
    encoded = base64.b64encode(imgByteArr)
    decoded = encoded.decode('ascii')
    return decoded


# get으로 바꾸어 사진 보여주기
@router.get("/show-people", description="face clustering으로 추출한 인물의 사진을 보여줍니다.")
async def show_people(id: UUID):
    # 사진 넣어주기
    people_img = {}
    people_img_name = {}
    result_path = os.path.join(FILE_DIR, str(id), 'result')
    dir_list = os.listdir(result_path)
    people_list = [dir for dir in dir_list if dir.startswith('person')]
    for person in people_list:
        # 현재는 첫 번째 이미지를 가져옴. 이후에 다른 이미지를 가져오는 알고리즘이 있다면 사용하기
        img_file = os.listdir(os.path.join(str(result_path), str(person)))[0]   # first_image
        img_path = os.path.join(str(result_path), str(person), str(img_file))
        img = Image.open(img_path)
        people_img[person] = from_img_to_bytes(img)
        people_img_name[person] = str(img_file)

    return {"id": id, "people_img": people_img, "people_img_name" : people_img_name}


@router.post("/timeline-face", description="face recognition을 통해 인물의 timeline을 추출한다.")
async def get_timeline_face(info: dict):
    """face recognition을 통하여 인물의 timeline을 추출한다.

    Args:
        info (dict): request body
            id (str) : 영상을 구분할 수 있는 영상 고유의 UUID
            face (list) : face recognition을 진행할 사람들에 해당하는 list ex) ["person_00", "person_02"]


    Returns:
        Response (dict) : 영상에 대한 UUID와 인물에 대한 timeline을 제공
            id (str) : 영상을 구분할 수 있는 영상 고유의 UUID
            face_timelines (dict) : 특정 인물들에 대한 timeline을 list형태로 제공 ex) face_timelines : {"person_00" : [[]], "person_03" : [[]]}
    """
    
    result_path = os.path.join(FILE_DIR, info['id'])
    video = os.path.join(result_path, 'original.mp4')

    timelines = {}
    
    for face in info['face']:
        image_file = os.listdir(os.path.join(result_path, 'result', face))[0]

        image = os.path.join(result_path, 'result', face, image_file)

        timeline = FaceRecognition(video, [image])
        timelines[face] = timeline
    # FE에서 선택한 사람을 받아 face recognition 진행 예정
    return {"id" : info['id'], "face_timelines": timelines}


# TODO: /show-people (face clustering 결과 보여주기)
# TODO: /timeline-face (face recognition을 통해 인물의 timeline 추출하기)
