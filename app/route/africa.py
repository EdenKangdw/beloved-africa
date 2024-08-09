from datetime import datetime, timedelta
import logging
import os
import shutil
import uuid
import ffmpeg
import base64


from fastapi import (
    APIRouter,
    Body,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer
from database.query import add_check, get_check
from database.schema import Check
from util.auth import get_current_user
from database.conn import db
from config import Config
from sqlalchemy.orm import Session
from PIL import Image

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# get config
config = Config()
app = APIRouter()

oauth2_scheme = HTTPBearer()

UPLOAD_DIR = "uploaded_videos"
THUMBNAIL_DIR = "thumbnails"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)


def generate_uuid_filename(extension):
    return f"{uuid.uuid4().hex}{extension}"


# file upload
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 파일을 원하는 위치에 저장
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = generate_uuid_filename(file_extension)
    file_path = f"{UPLOAD_DIR}/{unique_filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 비디오 파일 저장 경로 설정
    video_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 비디오 파일로부터 썸네일 생성
    thumbnail_path = os.path.join(
        THUMBNAIL_DIR, f"{os.path.splitext(unique_filename)[0]}.jpg"
    )
    generate_thumbnail_ffmpeg(video_path, thumbnail_path)

    return {
        "filename": unique_filename,
        "thumbnail": f"/africa/thumbnail/{os.path.splitext(unique_filename)[0]}.jpg",
    }


def generate_thumbnail_ffmpeg(video_path, thumbnail_path):
    try:
        (
            ffmpeg.input(video_path, ss=1)  # 비디오 시작 후 1초 시점의 프레임을 캡처
            .output(
                thumbnail_path, vframes=1, s="100x100"
            )  # 하나의 프레임을 이미지로 출력
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(thumbnail_path)
    except ffmpeg.Error as e:
        print("Error:", e.stderr.decode())
        raise ValueError("썸네일 생성 중 오류가 발생했습니다.")


@app.get("/thumbnail/{filename}")
async def get_thumbnail(filename: str):
    print("Loading thumbnail")
    file_path = os.path.join(THUMBNAIL_DIR, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            encoded_file = base64.b64encode(file_content).decode("utf-8")
            return JSONResponse(
                content={
                    "filename": filename,
                    "thumbnail": f"data:image/jpeg;base64,{encoded_file}",
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading thumbnail file")


# file download
@app.get("/download/{file_name}")
async def download_file(file_name):
    file_path = f"{THUMBNAIL_DIR}/{file_name}"
    return FileResponse(path=file_path, filename=file_name)
