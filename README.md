# FastAPI 학습 프로젝트

FastAPI를 활용한 단계별 백엔드 학습 프로젝트입니다. 메모리 저장소부터 DB, 인증, 비동기, 파일 업로드까지 핵심 개념을 단계별로 구현합니다.

---

## 프로젝트 구조

```
fastapi/
├── app/
│   ├── main.py              # FastAPI 앱 초기화 및 라우터 등록
│   ├── models.py            # SQLAlchemy ORM 모델 + 메모리용 dataclass
│   ├── schemas.py           # Pydantic 요청/응답 스키마
│   ├── database.py          # SQLite DB 설정 및 세션 관리
│   ├── auth.py              # JWT 인증 + bcrypt 비밀번호 해싱
│   ├── middleware.py        # 요청 로깅 미들웨어
│   ├── background.py        # 백그라운드 태스크 (이메일, 로그)
│   ├── repository.py        # 메모리 저장소 (Step 1)
│   ├── repository_db.py     # DB 저장소 (Step 2)
│   ├── services.py          # 비즈니스 로직 (메모리)
│   ├── services_db.py       # 비즈니스 로직 (DB)
│   ├── services_async.py    # 비동기 비즈니스 로직
│   ├── api/
│   │   ├── routes.py        # Step 1: 메모리 기반 CRUD (/api/...)
│   │   ├── routes_db.py     # Step 2: DB 기반 CRUD (/api/v2/...)
│   │   ├── routes_auth.py   # Step 3: JWT 인증 (/api/v3/...)
│   │   ├── routes_async.py  # Step 4: 비동기 처리 (/api/v4/...)
│   │   └── routes_upload.py # Step 6: 파일 업로드 (/api/v5/...)
│   ├── static/
│   │   ├── styles.css
│   │   └── app.js
│   └── templates/
│       └── index.html
├── tests/
│   └── test_api.py
├── uploads/                 # 업로드된 파일 저장 디렉토리
├── requirements.txt
├── TUTORIAL.md
└── README.md
```

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| 웹 프레임워크 | FastAPI 0.115 |
| ASGI 서버 | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| DB | SQLite (aiosqlite) |
| 인증 | JWT (python-jose) + bcrypt |
| 템플릿 | Jinja2 |
| 테스트 | pytest + httpx |

---

## 단계별 학습 내용

### Step 1 — 메모리 기반 CRUD (`/api/...`)
- `models.py`: 도메인 모델 (dataclass `Item`)
- `schemas.py`: Pydantic 입력/출력 스키마 (`ItemCreate`, `ItemUpdate`, `ItemResponse`)
- `repository.py`: 메모리 리스트 기반 저장소 패턴
- `services.py`: 비즈니스 로직 레이어 (중복 제목 검증 등)
- `api/routes.py`: CRUD 엔드포인트 (GET / POST / PUT / DELETE)

### Step 2 — SQLite DB 연동 (`/api/v2/...`)
- `database.py`: SQLAlchemy 엔진, 세션, Base 설정
- `models.py`: SQLAlchemy ORM 모델 (`ItemModel`)
- `repository_db.py`: DB 기반 저장소
- `services_db.py`: DB 서비스 레이어
- `api/routes_db.py`: DB 기반 CRUD 엔드포인트

### Step 3 — JWT 인증 (`/api/v3/...`)
- `auth.py`: JWT 토큰 발급/검증, bcrypt 비밀번호 해싱 (SHA-256 pre-hashing 포함)
- `middleware.py`: 요청 로깅 미들웨어 (`LoggingMiddleware`, `AuthHeaderMiddleware`)
- `api/routes_auth.py`: 회원가입, 로그인, 인증 필수 엔드포인트

### Step 4 — 비동기 처리 (`/api/v4/...`)
- `services_async.py`: `async/await` 기반 서비스, 동시 외부 API 호출
- `background.py`: `BackgroundTasks`로 응답 후 이메일 발송/로그 기록
- `api/routes_async.py`: 비동기 엔드포인트, 백그라운드 태스크 연동

### Step 5 — CORS & 전역 예외 처리
- `CORSMiddleware` 설정 (프론트엔드 연동 준비)
- `@app.exception_handler(ValueError)`: 전역 에러 핸들러

### Step 6 — 파일 업로드 (`/api/v5/...`)
- `api/routes_upload.py`: `UploadFile`로 이미지/문서 수신, 크기·확장자 검증, `uploads/` 디렉토리 저장

---

## 설치 및 실행

### 의존성 설치

```bash
pip install -r requirements.txt
```

### 서버 실행

```bash
uvicorn app.main:app --reload
```

서버는 기본적으로 `http://127.0.0.1:8000` 에서 실행됩니다.

### API 문서

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API 엔드포인트 요약

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/health` | 서버 상태 확인 |
| GET | `/api/items` | 아이템 목록 조회 (메모리) |
| POST | `/api/items` | 아이템 생성 (메모리) |
| GET | `/api/items/{id}` | 아이템 단건 조회 |
| PUT | `/api/items/{id}` | 아이템 수정 |
| DELETE | `/api/items/{id}` | 아이템 삭제 |
| GET | `/api/v2/items` | 아이템 목록 조회 (DB) |
| POST | `/api/v2/items` | 아이템 생성 (DB) |
| POST | `/api/v3/register` | 회원가입 |
| POST | `/api/v3/login` | 로그인 (JWT 발급) |
| GET | `/api/v3/items` | 인증 필수 아이템 조회 |
| GET | `/api/v4/async/items` | 비동기 아이템 조회 |
| POST | `/api/v4/async/items` | 비동기 + 백그라운드 생성 |
| POST | `/api/v5/upload` | 단일 파일 업로드 |
| POST | `/api/v5/upload/multiple` | 다중 파일 업로드 |
| GET | `/api/v5/files` | 업로드된 파일 목록 |

---

## 테스트 실행

```bash
pytest tests/ -v
```

커버리지 포함:

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

---

## 참고

자세한 구현 설명은 [TUTORIAL.md](TUTORIAL.md)를 참고하세요.
