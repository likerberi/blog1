from typing import Optional

from .models import Item
from .repository import ItemRepository
from .schemas import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        # 서비스는 비즈니스 규칙(검증/중복 체크)을 담당
        self._repository = repository

    def list_items(self):
        # 단순 조회는 저장소로 바로 위임
        return self._repository.list_items()

    def get_item(self, item_id: int):
        # 단건 조회
        return self._repository.get_item(item_id)

    def create_item(self, payload: ItemCreate):
        # 서비스 계층에서 중복 제목 검증
        self._ensure_title_unique(payload.title)
        return self._repository.create_item(payload.title, payload.description)

    def update_item(self, item_id: int, payload: ItemUpdate) -> Optional[Item]:
        item = self._repository.get_item(item_id)
        if item is None:
            return None
        # 제목이 변경될 경우에만 중복 체크
        if payload.title is not None and payload.title != item.title:
            self._ensure_title_unique(payload.title)
        return self._repository.update_item(
            item,
            title=payload.title,
            description=payload.description,
            is_done=payload.is_done,
        )

    def delete_item(self, item_id: int) -> bool:
        # 삭제 성공 여부만 반환
        return self._repository.delete_item(item_id)

    def reset(self) -> None:
        # 전체 초기화 (학습용)
        self._repository.reset()

    def _ensure_title_unique(self, title: str) -> None:
        # 같은 제목이 존재하면 예외 발생
        for existing in self._repository.list_items():
            if existing.title == title:
                raise ValueError("동일한 제목의 아이템이 이미 존재합니다.")
