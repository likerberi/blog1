"""
[Step 4] 백그라운드 태스크

핵심 학습 포인트:
1. BackgroundTasks로 응답 후 작업 실행
2. 이메일 발송, 로그 기록 등에 활용
3. 응답 속도 개선 (사용자는 즉시 응답 받음)
"""

import time
import logging
from datetime import datetime
from typing import List

from fastapi import BackgroundTasks

logger = logging.getLogger("fastapi_learning")


def write_log(message: str):
    """
    [백그라운드 로그 기록]
    
    응답 후에 실행되므로 사용자 대기 시간에 영향 없음
    """
    time.sleep(0.5)  # 파일 I/O 시뮬레이션
    logger.info(f"[백그라운드 로그] {datetime.utcnow().isoformat()} - {message}")
    
    # 실제로는 파일에 기록하거나 외부 로그 서비스로 전송
    with open("background_log.txt", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} - {message}\n")


def send_email_notification(email: str, subject: str, body: str):
    """
    [백그라운드 이메일 발송]
    
    실제로는 SMTP나 외부 서비스(SendGrid 등) 사용
    시간이 오래 걸리므로 백그라운드가 적합
    """
    logger.info(f"📧 이메일 발송 시작: {email}")
    time.sleep(2)  # 이메일 발송 시뮬레이션 (실제로는 2~5초 걸림)
    logger.info(f"📧 이메일 발송 완료: {email} | 제목: {subject}")
    
    # 발송 기록 저장
    with open("email_log.txt", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | To: {email} | Subject: {subject}\n")


def process_item_created(item_id: int, title: str):
    """
    [아이템 생성 후 처리]
    
    예: 검색 인덱스 업데이트, 캐시 갱신, 알림 발송 등
    """
    logger.info(f"🔄 아이템 생성 후 처리 시작: {item_id}")
    
    # 1. 검색 인덱스 업데이트 시뮬레이션
    time.sleep(0.3)
    logger.info(f"  - 검색 인덱스 업데이트 완료")
    
    # 2. 캐시 무효화 시뮬레이션
    time.sleep(0.2)
    logger.info(f"  - 캐시 무효화 완료")
    
    # 3. 알림 발송 시뮬레이션
    time.sleep(0.5)
    logger.info(f"  - 알림 발송 완료")
    
    logger.info(f"🔄 아이템 생성 후 처리 완료: {item_id} ({title})")


def cleanup_old_data():
    """
    [정기 정리 작업]
    
    오래된 데이터 삭제, 임시 파일 정리 등
    """
    logger.info("🧹 정리 작업 시작")
    time.sleep(1)
    logger.info("🧹 정리 작업 완료")


class NotificationService:
    """
    [알림 서비스 클래스]
    
    여러 백그라운드 작업을 조합해서 사용
    """
    
    @staticmethod
    def notify_item_created(
        background_tasks: BackgroundTasks,
        item_id: int,
        title: str,
        user_email: str = None,
    ):
        """아이템 생성 시 알림 처리"""
        # 로그 기록 (빠름)
        background_tasks.add_task(
            write_log,
            f"아이템 생성됨: {item_id} - {title}"
        )
        
        # 후처리 작업
        background_tasks.add_task(
            process_item_created,
            item_id,
            title
        )
        
        # 이메일 발송 (선택적)
        if user_email:
            background_tasks.add_task(
                send_email_notification,
                user_email,
                f"아이템 '{title}' 생성 완료",
                f"아이템 ID: {item_id}\n제목: {title}"
            )
