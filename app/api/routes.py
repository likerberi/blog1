from typing import List

from fastapi import APIRouter, HTTPException, status

from ..schemas import ItemCreate, ItemResponse, ItemUpdate
from ..services import ItemService


def create_router(service: ItemService) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["learning"])

    @router.get("/health")
    def health_check():
        # 가장 단순한 엔드포인트: 서버가 살아있는지 확인
        return {"status": "ok"}

    @router.get("/items", response_model=List[ItemResponse])
    def list_items():
        # 서비스 계층으로 위임 (요청 → 서비스 → 저장소)
        return service.list_items()

    @router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
    def create_item(payload: ItemCreate):
        # 입력 검증은 Pydantic이 수행하고, 비즈니스 규칙은 서비스가 처리
        try:
            return service.create_item(payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/items/{item_id}", response_model=ItemResponse)
    def get_item(item_id: int):
        # 경로 파라미터를 받아 서비스 호출
        item = service.get_item(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
        return item

    @router.put("/items/{item_id}", response_model=ItemResponse)
    def update_item(item_id: int, payload: ItemUpdate):
        # 업데이트 로직도 서비스로 위임
        try:
            item = service.update_item(item_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if item is None:
            raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
        return item

    @router.delete("/items/{item_id}")
    def delete_item(item_id: int):
        # 삭제 결과만 전달
        deleted = service.delete_item(item_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다.")
        return {"deleted": True, "id": item_id}

    @router.post("/reset")
    def reset_data():
        # 학습 편의를 위해 전체 초기화
        service.reset()
        return {"reset": True}

    return router
