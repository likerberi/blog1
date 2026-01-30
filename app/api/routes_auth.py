"""
[Step 3] 인증 라우터 (JWT 로그인 + 보호된 엔드포인트)

핵심 학습 포인트:
1. 로그인 → JWT 토큰 발급
2. Depends(get_current_user)로 인증 필수화
3. 인증된 사용자만 접근 가능한 엔드포인트
"""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserCreate,
    UserResponse,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_active_user,
)
from ..database import get_db
from ..schemas import ItemCreate, ItemResponse, ItemUpdate
from ..services_db import ItemDBService


router = APIRouter(prefix="/api/v3", tags=["인증 버전 (Step 3)"])


# ============================================================
# 의존성
# ============================================================

def get_item_service(db: Session = Depends(get_db)) -> ItemDBService:
    return ItemDBService(db)


# ============================================================
# 인증 엔드포인트
# ============================================================

@router.post("/register", response_model=UserResponse)
def register(payload: UserCreate):
    """
    회원가입
    
    비밀번호는 bcrypt로 해시되어 저장됨
    """
    try:
        user = create_user(payload.username, payload.password)
        return UserResponse(username=user["username"], is_active=user["is_active"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    로그인 → JWT 토큰 발급
    
    OAuth2PasswordRequestForm은 username/password를 form-data로 받음
    (Swagger UI에서 자동으로 로그인 폼 제공)
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 틀렸습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """
    [보호된 엔드포인트]
    
    Depends(get_current_active_user)가 핵심!
    - Authorization 헤더에서 토큰 추출
    - 토큰 검증
    - 사용자 정보 반환
    
    토큰이 없거나 유효하지 않으면 401 에러
    """
    return UserResponse(
        username=current_user["username"],
        is_active=current_user["is_active"],
    )


# ============================================================
# 보호된 CRUD 엔드포인트
# ============================================================

@router.get("/protected/items", response_model=List[ItemResponse])
def list_items_protected(
    service: ItemDBService = Depends(get_item_service),
    current_user: dict = Depends(get_current_active_user),  # 인증 필수!
):
    """
    [인증 필수] 전체 아이템 조회
    
    current_user 파라미터가 있으면 자동으로 인증 체크
    """
    return service.list_items()


@router.post("/protected/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item_protected(
    payload: ItemCreate,
    service: ItemDBService = Depends(get_item_service),
    current_user: dict = Depends(get_current_active_user),
):
    """[인증 필수] 아이템 생성"""
    try:
        return service.create_item(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/protected/items/{item_id}", response_model=ItemResponse)
def get_item_protected(
    item_id: int,
    service: ItemDBService = Depends(get_item_service),
    current_user: dict = Depends(get_current_active_user),
):
    """[인증 필수] 단건 조회"""
    item = service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    return item


@router.put("/protected/items/{item_id}", response_model=ItemResponse)
def update_item_protected(
    item_id: int,
    payload: ItemUpdate,
    service: ItemDBService = Depends(get_item_service),
    current_user: dict = Depends(get_current_active_user),
):
    """[인증 필수] 수정"""
    try:
        item = service.update_item(item_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if item is None:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    return item


@router.delete("/protected/items/{item_id}")
def delete_item_protected(
    item_id: int,
    service: ItemDBService = Depends(get_item_service),
    current_user: dict = Depends(get_current_active_user),
):
    """[인증 필수] 삭제"""
    deleted = service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
    return {"deleted": True, "id": item_id, "deleted_by": current_user["username"]}
