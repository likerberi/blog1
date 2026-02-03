# FastAPI 프로젝트 처음부터 만들기 가이드

이 문서는 FastAPI 프로젝트를 **왜 이런 구조로 나누는지**, **어디서부터 시작하는지** 단계별로 설명합니다.

---

## 📋 전체 흐름 요약

```
1단계: 데이터 구조 정의 (models.py, schemas.py)
2단계: 데이터 저장소 (repository.py)
3단계: 비즈니스 로직 (services.py)
4단계: API 엔드포인트 (api/routes.py)
5단계: 앱 초기화 (main.py)
6단계: UI 연결 (templates, static)
```

---

## 1단계: 데이터 구조 정의

### 왜 먼저 하나?
**"어떤 데이터를 다룰지"**가 명확해야 나머지를 만들 수 있습니다.

### 파일: `app/models.py`
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Item:
    id: int
    title: str
    description: Optional[str]
    is_done: bool
    created_at: datetime
    updated_at: datetime
```

**역할**: 내부에서 사용하는 데이터 모델(도메인 객체)

### 파일: `app/schemas.py`
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_done: Optional[bool] = None

class ItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_done: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**역할**: API 입출력 검증 스키마(Pydantic이 자동으로 검증)

**왜 분리?**  
- `models.py`: 내부 로직에서 사용  
- `schemas.py`: 외부(API 요청/응답)에서 사용  
- 관심사 분리 + 검증 자동화

---

## 2단계: 데이터 저장소

### 왜 이 단계?
**"데이터를 어디에 어떻게 저장할지"** 결정. DB/메모리/파일 등 저장 방식을 캡슐화.

### 파일: `app/repository.py`
```python
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
```

**역할**: 데이터 CRUD 전담 (Create, Read, Update, Delete)

**장점**: 나중에 DB로 바꾸려면 이 파일만 수정하면 됨

---

## 3단계: 비즈니스 로직 (서비스)

### 왜 필요?
**"어떤 규칙으로 데이터를 처리할지"** 정의. 검증, 중복 체크 등.

### 파일: `app/services.py`
```python
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
```

**역할**: 저장소를 사용하되, **비즈니스 규칙**(중복 체크, 권한 검증 등)을 추가

**왜 분리?**  
- Repository: 순수 데이터 처리  
- Service: 규칙/정책 처리

---

## 4단계: API 엔드포인트 (라우터)

### 왜 이제?
**"외부에서 어떻게 접근할지"** 정의. HTTP 요청을 서비스로 전달.

### 파일: `app/api/routes.py`
```python
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
```

**역할**: HTTP 요청을 받아 서비스로 전달, 응답 반환

**FastAPI 특징**:  
- 타입 힌트로 자동 검증  
- `response_model`로 응답 직렬화  
- 자동 문서 생성(`/docs`)

---

## 5단계: 앱 초기화

### 파일: `app/main.py`
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api.routes import create_router
from .repository import ItemRepository
from .services import ItemService

app = FastAPI(title="FastAPI 학습 프로젝트", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 의존성 주입: Repository → Service → Router
repository = ItemRepository()
service = ItemService(repository)
app.include_router(create_router(service))

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

**역할**: 모든 레이어를 연결하고 앱 부팅

**흐름**:  
1. Repository 생성  
2. Service에 주입  
3. Router에 주입  
4. FastAPI에 등록

---

## 6단계: UI 연결 (선택)

### 파일: `app/templates/index.html`, `app/static/app.js`

버튼 클릭 → JS fetch → 라우터 → 서비스 → 저장소 → 응답 → 화면 표시

---

## ✅ 작성 순서 요약

```
1. schemas.py (데이터 구조)
   ↓
2. repository.py (저장소)
   ↓
3. services.py (비즈니스 로직)
   ↓
4. api/routes.py (엔드포인트)
   ↓
5. main.py (앱 초기화)
   ↓
6. UI (선택)
```

---

## 🔑 핵심 구분점

| 항목 | FastAPI | Node.js Express | NestJS |
|------|---------|-----------------|--------|
| 타입 힌트 기반 검증 | ✅ Pydantic | ❌ 수동 | ✅ class-validator |
| 자동 문서화 | ✅ `/docs` | ❌ 수동 | ✅ Swagger 연동 |
| 비동기 기본 지원 | ✅ async/await | ✅ | ✅ |
| 레이어 분리 강제 | ❌ 자유 | ❌ 자유 | ✅ DI 기반 |

---

## 🚀 다음 단계

- `/docs` 접속해서 Swagger UI 확인
- 각 엔드포인트 하나씩 테스트
- 코드 파일 순서대로 읽으면서 흐름 파악

---

# Step 2: 의존성 주입 + DB 연동

## 📋 이 단계에서 배우는 것

1. **의존성 주입 (Depends)** - FastAPI 핵심 패턴
2. **SQLAlchemy ORM** - 파이썬 대표 ORM
3. **DB 세션 관리** - 요청마다 독립된 세션

## 📁 새로 추가된 파일

```
app/
├── database.py      # DB 연결 설정 + get_db() 의존성
├── models.py        # SQLAlchemy 모델 추가
├── repository_db.py # DB 저장소
├── services_db.py   # DB 서비스
└── api/
    └── routes_db.py # /api/v2/... 엔드포인트
```

## 🔑 핵심 개념: 의존성 주입 (Depends)

### 왜 필요한가?

```python
# ❌ 안 좋은 방식: 함수 안에서 직접 생성
@router.get("/items")
def get_items():
    db = SessionLocal()  # 매번 직접 생성
    try:
        # ... 로직
    finally:
        db.close()  # 매번 직접 정리
```

```python
# ✅ 좋은 방식: Depends로 주입
@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    # db는 자동으로 주입되고, 요청 끝나면 자동 정리
    # ... 로직만 작성
```

### 의존성 체인

```
요청 들어옴
    ↓
Depends(get_db) → DB 세션 생성
    ↓
Depends(get_item_service) → 서비스 인스턴스 생성
    ↓
라우터 함수 실행
    ↓
요청 완료 → 자동 정리 (finally 블록)
```

### 실제 코드 (app/database.py)

```python
def get_db():
    db = SessionLocal()
    try:
        yield db      # ← 여기서 세션을 "빌려줌"
    finally:
        db.close()    # ← 요청 끝나면 자동 정리
```

### 실제 코드 (app/api/routes_db.py)

```python
def get_item_service(db: Session = Depends(get_db)) -> ItemDBService:
    # get_db()가 먼저 실행되어 db를 받고,
    # 그 db로 서비스를 만들어서 반환
    return ItemDBService(db)

@router.get("/items")
def list_items(service: ItemDBService = Depends(get_item_service)):
    # service는 자동 주입됨
    return service.list_items()
```

## 🔄 메모리 vs DB 비교

| 항목 | 메모리 (Step 1) | DB (Step 2) |
|------|-----------------|-------------|
| 저장 위치 | Python dict | SQLite 파일 |
| 서버 재시작 시 | 데이터 사라짐 | 데이터 유지 |
| 세션 관리 | 없음 | Depends로 자동 |
| 경로 | /api/... | /api/v2/... |
| 버튼 색상 | 파랑 | 초록 |

## ✅ 확인 방법

1. 서버 실행: `uvicorn app.main:app --reload`
2. http://127.0.0.1:8000 접속
3. **초록색 버튼** (Step 2)으로 아이템 생성
4. 서버 종료 후 재시작
5. 다시 조회 → 데이터가 유지됨!
6. `/docs`에서 v2 API 확인
---

## Step 5: 에러 핸들링 + CORS

**목표**: 전역 예외 처리와 CORS 설정으로 프론트엔드 통합 준비

### 📌 왜 필요한가?

1. **에러 핸들링**: 예외 발생 시 일관된 응답 형식 제공
2. **CORS**: 다른 도메인(예: localhost:3000)에서 API 호출 허용

### 1️⃣ CORS 설정 (`app/main.py`)

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI 학습 프로젝트 v5.0", version="5.0.0")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 등 프론트엔드
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE 등 모든 메서드
    allow_headers=["*"],  # 모든 헤더 허용
)
```

**역할**:
- 브라우저의 CORS 정책을 우회하여 다른 포트의 프론트엔드가 API 호출 가능
- `allow_credentials=True`: 쿠키/인증 헤더 포함 요청 허용

### 2️⃣ 전역 예외 핸들러 (`app/main.py`)

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """ValueError → 400 Bad Request 변환"""
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "type": "validation_error"}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 Not Found 커스텀 응답"""
    return JSONResponse(
        status_code=404,
        content={"error": "요청한 리소스를 찾을 수 없습니다", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500 Internal Server Error 커스텀 응답"""
    return JSONResponse(
        status_code=500,
        content={"error": "서버 내부 오류가 발생했습니다", "type": str(type(exc).__name__)}
    )
```

**역할**:
- `ValueError` 발생 시 자동으로 400 에러로 변환
- 404, 500 에러 응답 형식 통일
- 프론트엔드에서 에러 처리가 쉬워짐

### 3️⃣ 에러 테스트 UI

**HTML** (`app/templates/index.html`):
```html
<section class="card">
  <h2>에러 핸들링 테스트 (Step 5)</h2>
  <p class="hint">전역 예외 핸들러 + CORS 설정 확인</p>
  <div class="button-grid error-buttons">
    <button data-action="test_duplicate">1. 중복 에러 발생</button>
    <button data-action="test_not_found">2. 404 에러</button>
    <button data-action="test_validation">3. 검증 에러</button>
  </div>
</section>
```

**JavaScript** (`app/static/app.js`):
```javascript
test_duplicate: async () => {
  // 같은 타이틀로 두 번 생성해서 ValueError 발생
  await fetchJsonWithAuth("/api/v3/items", {
    method: "POST",
    body: { title: "중복테스트", description: "첫 번째" },
  });
  return fetchJsonWithAuth("/api/v3/items", {
    method: "POST",
    body: { title: "중복테스트", description: "두 번째 (에러!)" },
  });
},
test_not_found: () => fetchJsonWithAuth("/api/v3/items/99999"),
test_validation: () =>
  fetchJson("/api/items", {
    method: "POST",
    body: { description: "title 필드 없음!" },
  }),
```

### 🎯 예외 흐름

```
[중복 에러]
1. 사용자: 같은 타이틀로 두 번 생성
2. services_db.py: raise ValueError("이미 존재하는 제목")
3. main.py: ValueError 핸들러 → 400 반환
4. 프론트엔드: {"error": "이미 존재하는 제목", "type": "validation_error"}

[404 에러]
1. 사용자: 존재하지 않는 ID로 조회
2. repository_db.py: raise HTTPException(status_code=404)
3. main.py: 404 핸들러 → 커스텀 메시지
4. 프론트엔드: {"error": "요청한 리소스를 찾을 수 없습니다", "path": "..."}

[검증 에러]
1. 사용자: title 필드 없이 생성 요청
2. FastAPI: Pydantic 검증 실패 → 자동으로 422 반환
3. 프론트엔드: {"detail": [{"loc": ["body", "title"], "msg": "field required"}]}
```

### 🔄 기존 코드와 비교

| 항목 | 이전 (Step 1-4) | 현재 (Step 5) |
|------|-----------------|---------------|
| 에러 응답 | 각 엔드포인트마다 다름 | 전역 핸들러로 통일 |
| CORS | 없음 (같은 도메인만) | localhost:3000 허용 |
| ValueError | 500 에러 | 400 Bad Request |
| 프론트엔드 연동 | 어려움 | 간단 |

### ✅ 확인 방법

1. 서버 실행: `uvicorn app.main:app --reload`
2. http://127.0.0.1:8000 접속
3. **먼저 로그인** (빨간색 버튼 Step 3)
4. **주황색 버튼** (Step 5)으로 에러 테스트:
   - "1. 중복 에러 발생" → 두 번 누르면 400 에러
   - "2. 404 에러" → 99999번 아이템 조회 실패
   - "3. 검증 에러" → title 없이 생성 시도 → 422 에러
5. 브라우저 개발자 도구 → Network 탭에서 CORS 헤더 확인