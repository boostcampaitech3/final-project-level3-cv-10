from fastapi import FastAPI, APIRouter
from ml.face_functions import FinalTimeline

router = APIRouter(tags=["highlight"])

@router.post("/timeline-highlight", description="최종 하이라이트에 해당하는 타임라인을 생성합니다.")
async def read_highlight(timelines: dict):
    print(timelines)
    face_timeline = timelines['face']
    laugh_timeline = timelines['laugh']
    id = timelines['id']

    make_shorts = FinalTimeline(laugh_timeline, face_timeline, id)


    return {"id" : id }