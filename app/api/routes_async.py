"""
[Step 4] 비동기 + 백그라운드 태스크 라우터

핵심 학습 포인트:
1. async def 엔드포인트
2. BackgroundTasks 의존성 주입
3. 동시 처리 vs 순차 처리 비교
"""

import asyncio
import time
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..background import NotificationService, send_email_notification, write_log
from ..database import get_db
from ..schemas import ItemCreate, ItemResponse
from ..services_async import (
    AsyncItemService,
    fetch_multiple_items_concurrently,
    simulate_external_api_call,
)


router = APIRouter(prefix="/api/v4", tags=["비동기 버전 (Step 4)"])


# ============================================================
# 의존성
# ============================================================

def get_async_service(db: Session = Depends(get_db)) -> AsyncItemService:
    return AsyncItemService(db)


# ============================================================
# 비동기 엔드포인트
# ============================================================

@router.get("/async/items", response_model=List[ItemResponse])
async def list_items_async(service: AsyncItemService = Depends(get_async_service)):
    """
    [비동기 조회]
    
    async def로 정의하면 비동기 함수가 됨.
    내부에서 await로 비동기 작업 대기.
    """
    return await service.list_items_async()


@router.post("/async/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item_async(
    payload: ItemCreate,
    background_tasks: BackgroundTasks,  # 백그라운드 태스크 주입
    service: AsyncItemService = Depends(get_async_service),
):
    """
    [비동기 생성 + 백그라운드 태스크]
    
    1. 아이템 생성 (비동기)
    2. 응답 반환 (사용자는 여기서 응답 받음)
    3. 백그라운드에서 후처리 실행
    """
    try:
        item = await service.create_item_async(payload)
        
        # 백그라운드 태스크 등록 (응답 후 실행됨)
        NotificationService.notify_item_created(
            background_tasks,
            item.id,
            item.title,
        )
        
        return item
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ============================================================
# 동시 처리 vs 순차 처리 비교
# ============================================================

@router.get("/async/sequential")
async def fetch_sequential():
    """
    [순차 처리 - 느림]
    
    하나씩 순서대로 실행.
    총 시간 = 각 작업 시간의 합
    """
    start = time.time()
    
    # 순차 실행 (하나 끝나면 다음 시작)
    result1 = await simulate_external_api_call(1)
    result2 = await simulate_external_api_call(2)
    result3 = await simulate_external_api_call(3)
    
    elapsed = time.time() - start
    
    return {
        "type": "sequential",
        "elapsed_seconds": round(elapsed, 2),
        "message": f"3개 요청을 순차 처리: {elapsed:.2f}초 (약 1.5초 예상)",
        "results": [result1, result2, result3],
    }


@router.get("/async/concurrent")
async def fetch_concurrent():
    """
    [동시 처리 - 빠름!]
    
    asyncio.gather로 동시에 실행.
    총 시간 ≈ 가장 느린 작업 시간
    """
    start = time.time()
    
    # 동시 실행 (모두 동시에 시작)
    results = await fetch_multiple_items_concurrently([1, 2, 3])
    
    elapsed = time.time() - start
    
    return {
        "type": "concurrent",
        "elapsed_seconds": round(elapsed, 2),
        "message": f"3개 요청을 동시 처리: {elapsed:.2f}초 (약 0.5초 예상)",
        "results": results,
    }


# ============================================================
# 백그라운드 태스크 데모
# ============================================================

@router.post("/background/log")
async def background_log_demo(
    message: str,
    background_tasks: BackgroundTasks,
):
    """
    [백그라운드 로그 기록 데모]
    
    1. 즉시 응답 반환
    2. 백그라운드에서 로그 기록 (0.5초 걸림)
    
    사용자는 로그 기록 완료를 기다리지 않음!
    """
    background_tasks.add_task(write_log, message)
    
    return {
        "status": "accepted",
        "message": "로그 기록이 백그라운드에서 처리됩니다.",
        "your_message": message,
    }


@router.post("/background/email")
async def background_email_demo(
    email: str,
    subject: str,
    body: str,
    background_tasks: BackgroundTasks,
):
    """
    [백그라운드 이메일 발송 데모]
    
    실제 이메일은 2~5초 걸리지만,
    사용자는 즉시 응답을 받음!
    """
    background_tasks.add_task(
        send_email_notification,
        email,
        subject,
        body,
    )
    
    return {
        "status": "accepted",
        "message": "이메일이 백그라운드에서 발송됩니다.",
        "to": email,
        "subject": subject,
    }


@router.post("/background/multiple")
async def background_multiple_demo(
    item_title: str,
    user_email: str,
    background_tasks: BackgroundTasks,
):
    """
    [여러 백그라운드 태스크 데모]
    
    하나의 요청에 여러 백그라운드 작업 등록 가능.
    순서대로 실행됨.
    """
    # 가짜 아이템 ID
    fake_item_id = 999
    
    # 여러 백그라운드 태스크 등록
    NotificationService.notify_item_created(
        background_tasks,
        fake_item_id,
        item_title,
        user_email,
    )
    
    return {
        "status": "accepted",
        "message": "여러 작업이 백그라운드에서 순차 처리됩니다.",
        "tasks": [
            "1. 로그 기록",
            "2. 검색 인덱스 업데이트",
            "3. 캐시 무효화",
            "4. 알림 발송",
            "5. 이메일 발송",
        ],
    }
