from datetime import datetime
from typing import Optional

from .models import Item


class ItemRepository:
    def __init__(self) -> None:
        # 메모리 저장소 (앱 재시작 시 초기화됨)
        self._items: dict[int, Item] = {}
        self._next_id = 1

    def list_items(self) -> list[Item]:
        # 전체 목록 반환
        return list(self._items.values())

    def get_item(self, item_id: int) -> Optional[Item]:
        # 단건 조회
        return self._items.get(item_id)

    def create_item(self, title: str, description: Optional[str]) -> Item:
        # 새 아이템 생성
        now = datetime.utcnow()
        item = Item(
            id=self._next_id,
            title=title,
            description=description,
            is_done=False,
            created_at=now,
            updated_at=now,
        )
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update_item(
        self,
        item: Item,
        title: Optional[str],
        description: Optional[str],
        is_done: Optional[bool],
    ) -> Item:
        # 부분 업데이트 (None은 변경하지 않음)
        if title is not None:
            item.title = title
        if description is not None:
            item.description = description
        if is_done is not None:
            item.is_done = is_done
        item.updated_at = datetime.utcnow()
        return item

    def delete_item(self, item_id: int) -> bool:
        # 삭제 성공 여부 반환
        return self._items.pop(item_id, None) is not None

    def reset(self) -> None:
        # 메모리 전체 초기화
        self._items.clear()
        self._next_id = 1
