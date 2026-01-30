"""
[Step 2] DB 저장소 (SQLAlchemy 버전)

기존 메모리 저장소(repository.py)와 비교하면서 학습하세요.
- 메모리: dict에 저장
- DB: SQLAlchemy 세션으로 저장
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import ItemModel


class ItemDBRepository:
    """
    DB 기반 저장소
    
    의존성 주입으로 Session을 받아서 사용
    """
    
    def __init__(self, db: Session):
        # Depends(get_db)로 주입받은 세션
        self._db = db

    def list_items(self) -> List[ItemModel]:
        """전체 목록 조회"""
        return self._db.query(ItemModel).all()

    def get_item(self, item_id: int) -> Optional[ItemModel]:
        """단건 조회"""
        return self._db.query(ItemModel).filter(ItemModel.id == item_id).first()

    def get_item_by_title(self, title: str) -> Optional[ItemModel]:
        """제목으로 조회 (중복 체크용)"""
        return self._db.query(ItemModel).filter(ItemModel.title == title).first()

    def create_item(self, title: str, description: Optional[str]) -> ItemModel:
        """
        새 아이템 생성
        
        db.add() → 세션에 추가
        db.commit() → DB에 저장
        db.refresh() → 생성된 id 등 DB에서 다시 읽어오기
        """
        item = ItemModel(
            title=title,
            description=description,
            is_done=False,
        )
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def update_item(
        self,
        item: ItemModel,
        title: Optional[str],
        description: Optional[str],
        is_done: Optional[bool],
    ) -> ItemModel:
        """부분 업데이트"""
        if title is not None:
            item.title = title
        if description is not None:
            item.description = description
        if is_done is not None:
            item.is_done = is_done
        item.updated_at = datetime.utcnow()
        self._db.commit()
        self._db.refresh(item)
        return item

    def delete_item(self, item: ItemModel) -> bool:
        """삭제"""
        self._db.delete(item)
        self._db.commit()
        return True

    def delete_all(self) -> None:
        """전체 삭제 (학습용)"""
        self._db.query(ItemModel).delete()
        self._db.commit()
