"""
FastAPI 학습 프로젝트 테스트

pytest로 모든 API 엔드포인트를 테스트합니다.
"""

import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ============================================================
# Fixture
# ============================================================
@pytest.fixture
def client():
    """테스트용 클라이언트"""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """인증 토큰 생성"""
    # 회원가입
    client.post("/api/v3/register", json={
        "username": "testuser",
        "password": "testpass123"
    })
    # 로그인
    response = client.post("/api/v3/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    return response.json()["access_token"]


# ============================================================
# Step 1: 메모리 저장소 테스트
# ============================================================
def test_health_check(client):
    """상태 확인 엔드포인트 테스트"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_item(client):
    """아이템 생성 테스트"""
    response = client.post("/api/items", json={
        "title": "테스트 아이템",
        "description": "테스트 설명"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "테스트 아이템"
    assert data["id"] == 1


def test_list_items(client):
    """아이템 목록 조회 테스트"""
    # 아이템 2개 생성
    client.post("/api/items", json={"title": "아이템1"})
    client.post("/api/items", json={"title": "아이템2"})
    
    response = client.get("/api/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 2


def test_get_item(client):
    """단일 아이템 조회 테스트"""
    # 아이템 생성
    create_response = client.post("/api/items", json={"title": "조회 테스트"})
    item_id = create_response.json()["id"]
    
    # 조회
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "조회 테스트"


def test_update_item(client):
    """아이템 수정 테스트"""
    # 아이템 생성
    create_response = client.post("/api/items", json={"title": "수정 전"})
    item_id = create_response.json()["id"]
    
    # 수정
    response = client.put(f"/api/items/{item_id}", json={
        "title": "수정 후",
        "is_done": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "수정 후"
    assert data["is_done"] is True


def test_delete_item(client):
    """아이템 삭제 테스트"""
    # 아이템 생성
    create_response = client.post("/api/items", json={"title": "삭제 테스트"})
    item_id = create_response.json()["id"]
    
    # 삭제
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 200
    
    # 삭제 확인
    get_response = client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404


# ============================================================
# Step 2: DB 저장소 테스트
# ============================================================
def test_db_health_check(client):
    """DB 상태 확인"""
    response = client.get("/api/v2/health")
    assert response.status_code == 200
    assert response.json()["storage"] == "sqlite"


def test_db_create_item(client):
    """DB 아이템 생성"""
    import random
    random_title = f"DB 테스트 {random.randint(1000, 9999)}"
    response = client.post("/api/v2/items", json={
        "title": random_title,
        "description": "SQLite 저장"
    })
    assert response.status_code == 201
    assert response.json()["title"] == random_title


# ============================================================
# Step 3: 인증 테스트
# ============================================================
def test_register(client):
    """회원가입 테스트"""
    response = client.post("/api/v3/register", json={
        "username": "newuser",
        "password": "newpass123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_login(client):
    """로그인 테스트"""
    # 회원가입
    client.post("/api/v3/register", json={
        "username": "logintest",
        "password": "loginpass123"
    })
    
    # 로그인
    response = client.post("/api/v3/login", data={
        "username": "logintest",
        "password": "loginpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_protected_endpoint_without_token(client):
    """토큰 없이 보호된 엔드포인트 접근"""
    response = client.get("/api/v3/protected/items")
    assert response.status_code == 401


def test_protected_endpoint_with_token(client, auth_token):
    """토큰으로 보호된 엔드포인트 접근"""
    response = client.get("/api/v3/protected/items", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 200


def test_get_profile(client, auth_token):
    """프로필 조회"""
    response = client.get("/api/v3/me", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


# ============================================================
# Step 4: 비동기 테스트
# ============================================================
def test_async_sequential(client):
    """순차 처리 테스트"""
    response = client.get("/api/v4/async/sequential")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "sequential"
    assert data["elapsed_seconds"] >= 1.0  # 최소 1초 이상


def test_async_concurrent(client):
    """동시 처리 테스트"""
    response = client.get("/api/v4/async/concurrent")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "concurrent"
    assert data["elapsed_seconds"] < 1.0  # 1초 미만


def test_background_task(client):
    """백그라운드 태스크 테스트"""
    response = client.post("/api/v4/background/log?message=test")
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


# ============================================================
# Step 5: 에러 핸들링 테스트
# ============================================================
def test_validation_error(client):
    """검증 에러 테스트 (title 없음)"""
    response = client.post("/api/items", json={
        "description": "제목 없음"
    })
    assert response.status_code == 422  # Pydantic validation error


def test_not_found_error(client):
    """404 에러 테스트"""
    response = client.get("/api/items/99999")
    assert response.status_code == 404


def test_duplicate_error(client, auth_token):
    """중복 에러 테스트"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 첫 번째 생성
    client.post("/api/v3/protected/items", 
        json={"title": "중복테스트", "description": "첫번째"},
        headers=headers
    )
    
    # 두 번째 생성 (중복)
    response = client.post("/api/v3/protected/items",
        json={"title": "중복테스트", "description": "두번째"},
        headers=headers
    )
    assert response.status_code == 400  # ValueError → 400


# ============================================================
# Step 6: 파일 업로드 테스트
# ============================================================
def test_upload_file(client):
    """파일 업로드 테스트"""
    # 텍스트 파일 생성
    files = {"file": ("test.txt", b"Hello FastAPI", "text/plain")}
    
    response = client.post("/api/v5/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["size"] > 0


def test_upload_invalid_file_type(client):
    """허용되지 않는 파일 타입 업로드"""
    files = {"file": ("test.exe", b"malware", "application/x-msdownload")}
    
    response = client.post("/api/v5/upload", files=files)
    assert response.status_code == 400


def test_list_uploads(client):
    """업로드 파일 목록 조회"""
    response = client.get("/api/v5/uploads")
    assert response.status_code == 200
    assert "files" in response.json()
    assert "count" in response.json()


def test_clear_uploads(client):
    """업로드 파일 삭제"""
    response = client.delete("/api/v5/uploads/clear")
    assert response.status_code == 200
