"""
[Step 2] 데이터베이스 모델 (SQLAlchemy ORM)

기존 dataclass → SQLAlchemy 모델로 변경
실제 DB 테이블과 1:1 매핑됨
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .database import Base


# ============================================================
# SQLAlchemy 모델: DB 테이블과 직접 연결
# ============================================================
class ItemModel(Base):
    """
    items 테이블에 매핑되는 ORM 모델
    
    Column() 안에서:
    - primary_key: 기본키
    - index: 검색 성능용 인덱스
    - nullable: NULL 허용 여부
    - default: 기본값
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================
# 기존 dataclass 유지 (메모리 저장소용, 비교 학습용)
# ============================================================
from dataclasses import dataclass


@dataclass
class Item:
    """기존 메모리 저장소용 모델 (비교용으로 유지)"""
    id: int
    title: str
    description: Optional[str]
    is_done: bool
    created_at: datetime
    updated_at: datetime
