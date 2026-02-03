from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import create_router
from .api.routes_db import router as db_router  # [Step 2] DB 라우터 추가
from .api.routes_auth import router as auth_router  # [Step 3] 인증 라우터 추가
from .api.routes_async import router as async_router  # [Step 4] 비동기 라우터 추가
from .database import Base, engine  # [Step 2] DB 설정 추가
from .middleware import LoggingMiddleware, AuthHeaderMiddleware  # [Step 3] 미들웨어
from .repository import ItemRepository
from .services import ItemService

# [Step 2] DB 테이블 생성 (앱 시작 시 자동 실행)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI 학습 프로젝트", version="5.0.0")

# [Step 5] CORS 설정 (가장 먼저 등록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

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

# [Step 4] 비동기 + 백그라운드 라우터 추가
# /api/v4/... 경로로 접근 가능
app.include_router(async_router)


# ============================================================
# [Step 5] 전역 예외 핸들러
# ============================================================

from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    ValueError 전역 처리
    
    서비스 레이어에서 발생하는 비즈니스 로직 에러를
    일관된 형식으로 반환
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": "ValidationError",
            "message": str(exc),
            "path": request.url.path,
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """커스텀 404 에러"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "NotFound",
            "message": f"경로를 찾을 수 없습니다: {request.url.path}",
            "suggestion": "/docs 에서 사용 가능한 API를 확인하세요.",
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """서버 에러 처리"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "서버 내부 오류가 발생했습니다.",
            "path": request.url.path,
        },
    )


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
