"""
[Step 3] 미들웨어 (요청/응답 전처리)

미들웨어는 모든 요청에 대해 실행됨:
요청 → [미들웨어] → 라우터 → [미들웨어] → 응답

핵심 학습 포인트:
1. 요청 로깅
2. 응답 시간 측정
3. 요청/응답 변환
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_learning")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    [요청 로깅 미들웨어]
    
    모든 요청에 대해:
    1. 요청 시작 시간 기록
    2. 라우터 실행
    3. 응답 시간 계산 및 로깅
    """
    
    async def dispatch(self, request: Request, call_next):
        # 요청 시작
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        logger.info(f"→ 요청 시작: {method} {path}")
        
        # 다음 미들웨어 또는 라우터 실행
        response = await call_next(request)
        
        # 응답 시간 계산
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(f"← 응답 완료: {method} {path} | {response.status_code} | {process_time:.3f}초")
        
        return response


class AuthHeaderMiddleware(BaseHTTPMiddleware):
    """
    [인증 헤더 체크 미들웨어]
    
    특정 경로에 대해 Authorization 헤더 존재 여부만 로깅
    (실제 검증은 Depends에서 수행)
    """
    
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        path = request.url.path
        
        if path.startswith("/api/v3/protected"):
            if auth_header:
                logger.info(f"🔐 인증 헤더 감지: {path}")
            else:
                logger.warning(f"⚠️ 인증 헤더 없음: {path}")
        
        response = await call_next(request)
        return response
