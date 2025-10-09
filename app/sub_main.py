"""
Asset Manager 서브모듈 엔트리 포인트
리팩토링된 모듈형 구조
"""

import logging
import sys
import os
from fastapi import APIRouter

# 현재 모듈 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 로컬 모듈 import
from api.asset_router import router as asset_router
from api.report_router import router as report_router
from tasks.background_tasks import background_tasks

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asset-manager")

def get_router():
    """통합 라우터 반환"""
    # 메인 라우터 생성
    main_router = APIRouter()
    
    # 자산 관리 라우터 포함
    main_router.include_router(asset_router, tags=["Assets"])
    
    # 보고서 라우터 포함 (reports 접두사 추가)
    main_router.include_router(report_router, prefix="/reports", tags=["Reports"])
    
    logger.info("Asset Manager 라우터 통합 완료")
    return main_router

async def start_background_tasks():
    """백그라운드 태스크 시작"""
    await background_tasks.start_all_tasks()

# 모듈 초기화
logger.info("Asset Manager 모듈 초기화 완료")