"""
Asset Manager API 라우터
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.asset_models import Asset, AssetPortfolio
from services.asset_service import asset_service
from services.report_service import report_service
from typing import List

# 라우터 생성
router = APIRouter()

@router.get("/", tags=["Asset Manager"])
async def asset_manager_root():
    """Asset Manager 루트 엔드포인트"""
    return {
        "service": "Asset Manager",
        "version": "1.0.0",
        "description": "자산 관리 및 포트폴리오 추적 서비스",
        "endpoints": {
            "portfolio": "/asset-manager/portfolio",
            "assets": "/asset-manager/assets",
            "add_asset": "/asset-manager/assets (POST)",
            "sync": "/asset-manager/sync"
        }
    }

@router.get("/portfolio", response_model=AssetPortfolio, tags=["Portfolio"])
async def get_portfolio():
    """현재 포트폴리오 조회"""
    return asset_service.get_portfolio()

@router.get("/assets", response_model=List[Asset], tags=["Assets"])
async def get_assets():
    """모든 자산 목록 조회"""
    return asset_service.get_all_assets()

@router.post("/assets", response_model=Asset, tags=["Assets"])
async def add_asset(asset: Asset):
    """새 자산 추가"""
    return asset_service.create_asset(asset)

@router.put("/assets/{asset_id}", response_model=Asset, tags=["Assets"])
async def update_asset(asset_id: str, updated_asset: Asset):
    """자산 정보 업데이트"""
    try:
        return asset_service.update_asset(asset_id, updated_asset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/assets/{asset_id}", tags=["Assets"])
async def delete_asset(asset_id: str):
    """자산 삭제"""
    try:
        return asset_service.delete_asset(asset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/sync", tags=["Sync"])
async def sync_asset_prices(background_tasks: BackgroundTasks):
    """자산 가격 동기화 (백그라운드 작업)"""
    background_tasks.add_task(asset_service.sync_asset_prices)
    return {"message": "자산 가격 동기화가 시작되었습니다"}

@router.get("/health", tags=["Health"])
async def health_check():
    """Asset Manager 헬스 체크"""
    return asset_service.get_health_status()