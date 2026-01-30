"""
[Step 2] DB 서비스 (SQLAlchemy 버전)

기존 services.py와 비교하면서 학습하세요.
구조는 거의 동일하고, 저장소만 DB 버전으로 교체됨.
"""

from typing import Optional

from sqlalchemy.orm import Session

from .models import ItemModel
from .repository_db import ItemDBRepository
from .schemas import ItemCreate, ItemUpdate


class ItemDBService:
    """
    DB 기반 서비스
    
    저장소를 직접 생성하지 않고 Session을 받아서 저장소 생성
    → 의존성 주입 체인: Depends(get_db) → Service → Repository
    """
    
    def __init__(self, db: Session):
        # DB 세션으로 저장소 생성
        self._repository = ItemDBRepository(db)

    def list_items(self):
        return self._repository.list_items()

    def get_item(self, item_id: int):
        return self._repository.get_item(item_id)

    def create_item(self, payload: ItemCreate):
        # 중복 제목 체크
        self._ensure_title_unique(payload.title)
        return self._repository.create_item(payload.title, payload.description)

    def update_item(self, item_id: int, payload: ItemUpdate) -> Optional[ItemModel]:
        item = self._repository.get_item(item_id)
        if item is None:
            return None
        # 제목 변경 시 중복 체크
        if payload.title is not None and payload.title != item.title:
            self._ensure_title_unique(payload.title)
        return self._repository.update_item(
            item,
            title=payload.title,
            description=payload.description,
            is_done=payload.is_done,
        )

    def delete_item(self, item_id: int) -> bool:
        item = self._repository.get_item(item_id)
        if item is None:
            return False
        return self._repository.delete_item(item)

    def reset(self) -> None:
        self._repository.delete_all()

    def _ensure_title_unique(self, title: str) -> None:
        existing = self._repository.get_item_by_title(title)
        if existing:
            raise ValueError("동일한 제목의 아이템이 이미 존재합니다.")
