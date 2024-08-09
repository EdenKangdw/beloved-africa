#!/bin/sh

# debugpy 설치
pip install debugpy

# 애플리케이션 실행
exec python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
