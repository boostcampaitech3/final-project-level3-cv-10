from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse
from ml.face_functions import FinalTimeline

import os

router = APIRouter(tags=["highlight"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.join(BASE_DIR, 'files/')

@router.post("/timeline-highlight", description="최종 하이라이트에 해당하는 타임라인을 생성합니다.")
async def read_highlight(timelines: dict):
    """최종 하이라이트에 해당하는 쇼츠들을 생성한 후 google storage에 저장한 후, 파일명을 전달하여 client에서 접근할 수 있도록 한다.

    Args:
        timelines (dict): 크게 3개의 compoenet들이 있다.
            id (str) : 참조하려는 영상의 UUID
            face (dict) : 각각의 인물들에 대한 face recognition timeline을 가지고 있다. timeline은 2차원 list이다.
            laugh (list) : 2차원 list로 웃음에 해당하는 [시작, 끝, 흥미도]로 이루어져 있다.


    Returns:
        Response (dict) : id, shorts, people_img를 return 한다.
            id (str) : 특정 영상에 대한 UUID
            shorts (list) : 특정 등장인물에 대한 영상정보를 담고 있는 list이다.
                short (list) : [{등장 인물}, {영상 디렉토리}, {영상 길이}, {영상 흥미도}] 로 구성되어 있다.
            people_img (dict) : 선택한 인물들의 이미지 디렉토리를 dictionary형태로 담아서 제공한다. ex) "people_img" : {"person_00" : "people/person_00.png", "person_03" : "people/person_03.png"}
    """
    print(timelines)
    face_timeline = timelines['face']
    laugh_timeline = timelines['laugh']
    id = timelines['id']

    shorts = FinalTimeline(laugh_timeline, face_timeline, id)

    return {"id" : id, "shorts": shorts, "people_img" : {}}