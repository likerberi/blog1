"""
[Step 2] 데이터베이스 설정
- SQLAlchemy + SQLite 사용
- 의존성 주입(Depends)으로 세션 관리
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite 파일 기반 DB (app.db 파일 생성됨)
DATABASE_URL = "sqlite:///./app.db"

# 엔진 생성: DB와의 연결 담당
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 전용 설정
)

# 세션 팩토리: 요청마다 새 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 베이스 클래스
Base = declarative_base()


def get_db():
    """
    [의존성 주입용 함수]
    
    FastAPI의 Depends()에서 사용됨.
    요청이 들어오면 DB 세션을 생성하고,
    요청이 끝나면 자동으로 세션을 닫음.
    
    사용법:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db  # 여기서 세션을 "빌려줌"
    finally:
        db.close()  # 요청 끝나면 자동 정리
