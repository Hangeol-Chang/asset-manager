"""
보고서 API 라우터
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.report_service import report_service

# 라우터 생성
router = APIRouter()

@router.get("/monthly", tags=["Reports"])
async def get_monthly_reports():
    """월간 보고서 목록 조회"""
    try:
        return report_service.get_monthly_reports()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly/{year}/{month}", tags=["Reports"])
async def get_monthly_report(year: int, month: int):
    """특정 월의 상세 보고서 조회"""
    try:
        return report_service.get_monthly_report(year, month)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-monthly", tags=["Reports"])
async def generate_monthly_report_now(background_tasks: BackgroundTasks):
    """현재 시점의 월간 보고서 즉시 생성"""
    background_tasks.add_task(report_service.generate_monthly_report, True)
    return {"message": "월간 보고서 생성이 시작되었습니다"}