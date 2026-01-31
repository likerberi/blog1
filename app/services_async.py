"""
[Step 4] 비동기 서비스 (async/await)

핵심 학습 포인트:
1. async def vs def 차이
2. await로 비동기 작업 대기
3. 동시 처리 (asyncio.gather)
"""

import asyncio
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ItemModel
from .schemas import ItemCreate, ItemUpdate


class AsyncItemService:
    """
    비동기 서비스 예시
    
    주의: 실제로 비동기 DB를 사용하려면 
    AsyncSession + async engine이 필요함.
    여기서는 개념 학습용으로 sleep을 사용.
    """
    
    def __init__(self, db: Session):
        self._db = db

    async def list_items_async(self) -> List[ItemModel]:
        """
        [비동기 조회]
        
        실제로는 async DB 드라이버 사용:
        result = await session.execute(select(ItemModel))
        """
        # 네트워크 지연 시뮬레이션
        await asyncio.sleep(0.1)
        return self._db.query(ItemModel).all()

    async def get_item_async(self, item_id: int) -> Optional[ItemModel]:
        """비동기 단건 조회"""
        await asyncio.sleep(0.05)
        return self._db.query(ItemModel).filter(ItemModel.id == item_id).first()

    async def create_item_async(self, payload: ItemCreate) -> ItemModel:
        """
        [비동기 생성]
        
        I/O 작업(DB, 외부 API 등)에서 await 사용
        """
        # 중복 체크 (비동기)
        await self._ensure_title_unique_async(payload.title)
        
        # 생성
        item = ItemModel(
            title=payload.title,
            description=payload.description,
            is_done=False,
        )
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    async def _ensure_title_unique_async(self, title: str) -> None:
        """비동기 중복 체크"""
        await asyncio.sleep(0.05)
        existing = self._db.query(ItemModel).filter(ItemModel.title == title).first()
        if existing:
            raise ValueError("동일한 제목의 아이템이 이미 존재합니다.")


async def simulate_external_api_call(item_id: int) -> dict:
    """
    [외부 API 호출 시뮬레이션]
    
    실제로는 httpx.AsyncClient 등 사용:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    """
    await asyncio.sleep(0.5)  # 외부 API 응답 대기 시뮬레이션
    return {
        "item_id": item_id,
        "external_data": f"외부 API 응답 (item {item_id})",
        "fetched_at": datetime.utcnow().isoformat(),
    }


async def fetch_multiple_items_concurrently(item_ids: List[int]) -> List[dict]:
    """
    [동시 처리 예시]
    
    asyncio.gather로 여러 비동기 작업을 동시에 실행
    순차 실행보다 훨씬 빠름!
    """
    # 모든 요청을 동시에 시작하고 결과 대기
    results = await asyncio.gather(
        *[simulate_external_api_call(item_id) for item_id in item_ids]
    )
    return results
