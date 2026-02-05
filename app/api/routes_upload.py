"""
[Step 6] 파일 업로드 라우터

핵심 학습 포인트:
1. UploadFile로 파일 받기
2. 파일 크기/타입 검증
3. 파일 저장 및 경로 반환
"""

import os
import shutil
from datetime import datetime
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel


router = APIRouter(prefix="/api/v5", tags=["Step 6: File Upload"])


# ============================================================
# 설정
# ============================================================
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".csv"}

# uploads 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# 스키마
# ============================================================
class FileUploadResponse(BaseModel):
    filename: str
    filepath: str
    size: int
    content_type: str
    uploaded_at: str


class MultipleFilesResponse(BaseModel):
    files: List[FileUploadResponse]
    total_size: int


# ============================================================
# 헬퍼 함수
# ============================================================
def validate_file(file: UploadFile) -> None:
    """파일 검증: 크기 및 확장자"""
    # 파일 확장자 검증
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않는 파일 타입입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def save_upload_file(upload_file: UploadFile) -> tuple[str, int]:
    """
    업로드된 파일을 저장하고 경로 반환
    
    Returns:
        (파일경로, 파일크기) 튜플
    """
    # 고유 파일명 생성 (타임스탬프 추가)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{upload_file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # 파일 저장
    file_size = 0
    with open(filepath, "wb") as buffer:
        chunk_size = 8192  # 8KB씩 읽기
        while True:
            chunk = upload_file.file.read(chunk_size)
            if not chunk:
                break
            
            file_size += len(chunk)
            
            # 파일 크기 제한 체크
            if file_size > MAX_FILE_SIZE:
                # 파일 삭제하고 에러
                os.remove(filepath)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"파일 크기가 너무 큽니다 (최대: {MAX_FILE_SIZE / 1024 / 1024}MB)"
                )
            
            buffer.write(chunk)
    
    return filepath, file_size


# ============================================================
# 엔드포인트
# ============================================================
@router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def upload_file(file: UploadFile = File(..., description="업로드할 파일")):
    """
    단일 파일 업로드
    
    - **file**: 업로드할 파일 (최대 5MB)
    - 허용 확장자: jpg, jpeg, png, gif, pdf, txt, csv
    """
    # 파일 검증
    validate_file(file)
    
    # 파일 저장
    filepath, file_size = save_upload_file(file)
    
    return FileUploadResponse(
        filename=file.filename,
        filepath=filepath,
        size=file_size,
        content_type=file.content_type or "unknown",
        uploaded_at=datetime.now().isoformat()
    )


@router.post("/upload/multiple", response_model=MultipleFilesResponse, status_code=201)
async def upload_multiple_files(files: List[UploadFile] = File(..., description="업로드할 파일들")):
    """
    여러 파일 동시 업로드
    
    - **files**: 업로드할 파일 리스트 (각 파일 최대 5MB)
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="한 번에 최대 10개 파일만 업로드 가능합니다"
        )
    
    uploaded_files = []
    total_size = 0
    
    for file in files:
        # 파일 검증
        validate_file(file)
        
        # 파일 저장
        filepath, file_size = save_upload_file(file)
        total_size += file_size
        
        uploaded_files.append(
            FileUploadResponse(
                filename=file.filename,
                filepath=filepath,
                size=file_size,
                content_type=file.content_type or "unknown",
                uploaded_at=datetime.now().isoformat()
            )
        )
    
    return MultipleFilesResponse(
        files=uploaded_files,
        total_size=total_size
    )


@router.get("/uploads")
async def list_uploads():
    """업로드된 파일 목록 조회"""
    if not os.path.exists(UPLOAD_DIR):
        return {"files": [], "count": 0}
    
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                "filename": filename,
                "size": stat.st_size,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    return {
        "files": sorted(files, key=lambda x: x["uploaded_at"], reverse=True),
        "count": len(files)
    }


@router.delete("/uploads/clear")
async def clear_uploads():
    """업로드된 파일 모두 삭제 (테스트용)"""
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    return {"message": "모든 업로드 파일이 삭제되었습니다"}
