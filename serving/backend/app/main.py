import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api import video, face, laughter

app = FastAPI()

app.include_router(video.router)
app.include_router(face.router)
app.include_router(laughter.router)

origins = [
    "http://34.64.107.58:30002",
    "34.64.107.58:30002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def read_root() -> dict:
    return {"message": "Welcome to SNOWMAN :')"}


if __name__ == "__main__":
    # uvicorn.run("api.api:app", host="0.0.0.0", port=30001, reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=30001, reload=True)
