"""
[Step 3] 인증 모듈 (JWT + 비밀번호 해싱)

핵심 학습 포인트:
1. JWT 토큰 생성/검증
2. 비밀번호 해싱 (bcrypt)
3. Depends로 인증 주입
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


# ============================================================
# 설정 (실제 프로젝트에서는 환경변수로 관리)
# ============================================================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================================
# 비밀번호 해싱
# ============================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 비밀번호와 해시된 비밀번호 비교"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호를 해시로 변환 (저장용)"""
    return pwd_context.hash(password)


# ============================================================
# 스키마
# ============================================================
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    is_active: bool


# ============================================================
# 간단한 메모리 유저 저장소 (학습용)
# ============================================================
fake_users_db: dict = {}


def get_user(username: str) -> Optional[dict]:
    return fake_users_db.get(username)


def create_user(username: str, password: str) -> dict:
    if username in fake_users_db:
        raise ValueError("이미 존재하는 사용자입니다.")
    hashed = get_password_hash(password)
    user = {
        "username": username,
        "hashed_password": hashed,
        "is_active": True,
    }
    fake_users_db[username] = user
    return user


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """사용자 인증: 아이디/비밀번호 확인"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


# ============================================================
# JWT 토큰
# ============================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성
    
    data에 사용자 정보(sub=username)를 담고,
    만료 시간(exp)을 추가해서 서명
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============================================================
# 의존성: 현재 사용자 가져오기
# ============================================================

# OAuth2 스킴: Authorization 헤더에서 토큰 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v3/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    [인증 의존성]
    
    1. oauth2_scheme이 Authorization 헤더에서 토큰 추출
    2. 토큰 검증 및 디코딩
    3. 사용자 정보 반환
    
    사용법:
        @router.get("/protected")
        def protected_route(user: dict = Depends(get_current_user)):
            # user는 인증된 사용자 정보
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 사용자 조회
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """활성 사용자만 허용"""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="비활성 사용자입니다.")
    return current_user
