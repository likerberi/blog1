"""
[Step 2] DB 라우터 (의존성 주입 버전)

핵심 학습 포인트: Depends() 사용법

기존 routes.py와 비교:
- 기존: 서비스를 함수 인자로 받음
- DB 버전: Depends(get_db)로 세션을 주입받아 서비스 생성
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ItemCreate, ItemResponse, ItemUpdate
from ..services_db import ItemDBService


# ============================================================
# 의존성 주입 함수들
# ============================================================

def get_item_service(db: Session = Depends(get_db)) -> ItemDBService:
    """
    [의존성 주입 체인]
    
    1. FastAPI가 get_db()를 호출 → DB 세션 생성
    2. 그 세션을 get_item_service()에 전달
    3. 서비스 인스턴스 반환
    
    이렇게 하면 각 요청마다 독립된 세션과 서비스가 생성됨
    """
    return ItemDBService(db)


# ============================================================
# 라우터 정의
# ============================================================

router = APIRouter(prefix="/api/v2", tags=["DB 버전 (Step 2)"])


@router.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok", "version": "v2", "storage": "sqlite"}


@router.get("/items", response_model=List[ItemResponse])
def list_items(service: ItemDBService = Depends(get_item_service)):
    """
    [Depends 사용 예시]
    
    service 파라미터에 Depends()를 붙이면:
    1. FastAPI가 get_item_service() 호출
    2. 반환된 서비스 인스턴스가 service에 할당됨
    3. 함수 실행 후 자동 정리
    """
    return service.list_items()


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    service: ItemDBService = Depends(get_item_service)
):
    """아이템 생성"""
    try:
        return service.create_item(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    service: ItemDBService = Depends(get_item_service)
):
    """단건 조회"""
    item = service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    return item


@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    service: ItemDBService = Depends(get_item_service)
):
    """수정"""
    try:
        item = service.update_item(item_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    return item


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    service: ItemDBService = Depends(get_item_service)
):
    """삭제"""
    deleted = service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    return {"deleted": True, "id": item_id}


@router.post("/reset")
def reset_data(service: ItemDBService = Depends(get_item_service)):
    """전체 초기화"""
    service.reset()
    return {"reset": True}
