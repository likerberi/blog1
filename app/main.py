from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api.routes import create_router
from .api.routes_db import router as db_router  # [Step 2] DB 라우터 추가
from .api.routes_auth import router as auth_router  # [Step 3] 인증 라우터 추가
from .database import Base, engine  # [Step 2] DB 설정 추가
from .middleware import LoggingMiddleware, AuthHeaderMiddleware  # [Step 3] 미들웨어
from .repository import ItemRepository
from .services import ItemService

# [Step 2] DB 테이블 생성 (앱 시작 시 자동 실행)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI 학습 프로젝트", version="3.0.0")

# [Step 3] 미들웨어 등록 (순서 중요: 먼저 등록한 것이 바깥쪽)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthHeaderMiddleware)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# [Step 1] 메모리 기반 라우터 (기존 유지)
repository = ItemRepository()
service = ItemService(repository)
app.include_router(create_router(service))

# [Step 2] DB 기반 라우터 추가
# /api/v2/... 경로로 접근 가능
app.include_router(db_router)

# [Step 3] 인증 기반 라우터 추가
# /api/v3/... 경로로 접근 가능
app.include_router(auth_router)


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
