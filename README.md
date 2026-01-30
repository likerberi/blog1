# FastAPI 학습용 프로젝트

버튼을 하나씩 눌러 FastAPI 요청/응답 흐름을 확인할 수 있는 학습용 프로젝트입니다.

## 빠른 시작

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

브라우저에서 http://127.0.0.1:8000 으로 접속해 버튼을 눌러 확인하세요.  
API 문서는 http://127.0.0.1:8000/docs 에서 확인 가능합니다.

## 학습 자료

**처음부터 만드는 방법**은 [TUTORIAL.md](TUTORIAL.md)를 참고하세요.  
- 왜 이런 구조로 나누는지  
- 어디서부터 작성하는지  
- 각 레이어의 역할  

## 프로젝트 구조

```
app/
├── main.py              # 앱 엔트리포인트
├── models.py            # 도메인 모델
├── schemas.py           # API 입출력 스키마 (Pydantic)
├── repository.py        # 데이터 저장소
├── services.py          # 비즈니스 로직
├── api/
│   └── routes.py        # API 엔드포인트
├── templates/
│   └── index.html       # UI
└── static/
    ├── app.js           # 프론트엔드 로직
    └── styles.css       # 스타일
```

## 학습 포인트

- 라우터 → 서비스 → 저장소 레이어 분리
- Pydantic 스키마로 자동 입력 검증
- 타입 힌트 기반 개발
- 자동 API 문서화 (`/docs`)
