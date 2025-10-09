"""
Asset Manager 서브모듈
자산 관리 기능을 제공하는 FastAPI 라우터와 백그라운드 태스크
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import asyncio
import logging
from datetime import datetime
from typing import List, Optional
import json
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asset-manager")

# 데이터 모델
class Asset(BaseModel):
    id: Optional[str] = None
    name: str
    type: str  # 'stock', 'crypto', 'real_estate', 'cash', etc.
    value: float
    currency: str = "KRW"
    last_updated: Optional[datetime] = None

class AssetPortfolio(BaseModel):
    total_value: float
    assets: List[Asset]
    last_sync: datetime

# 메모리 데이터 저장소 (실제로는 DB 연결 필요)
asset_data = {
    "portfolio": {
        "total_value": 0.0,
        "assets": [],
        "last_sync": datetime.now()
    }
}

# FastAPI 라우터 생성
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
    portfolio = asset_data["portfolio"]
    return AssetPortfolio(
        total_value=portfolio["total_value"],
        assets=[Asset(**asset) for asset in portfolio["assets"]],
        last_sync=portfolio["last_sync"]
    )

@router.get("/assets", response_model=List[Asset], tags=["Assets"])
async def get_assets():
    """모든 자산 목록 조회"""
    return [Asset(**asset) for asset in asset_data["portfolio"]["assets"]]

@router.post("/assets", response_model=Asset, tags=["Assets"])
async def add_asset(asset: Asset):
    """새 자산 추가"""
    # ID 생성
    asset.id = f"asset_{len(asset_data['portfolio']['assets']) + 1}"
    asset.last_updated = datetime.now()
    
    # 자산 추가
    asset_dict = asset.dict()
    asset_data["portfolio"]["assets"].append(asset_dict)
    
    # 총 가치 업데이트
    update_total_value()
    
    logger.info(f"새 자산 추가됨: {asset.name} - {asset.value} {asset.currency}")
    return asset

@router.put("/assets/{asset_id}", response_model=Asset, tags=["Assets"])
async def update_asset(asset_id: str, updated_asset: Asset):
    """자산 정보 업데이트"""
    for i, asset in enumerate(asset_data["portfolio"]["assets"]):
        if asset["id"] == asset_id:
            updated_asset.id = asset_id
            updated_asset.last_updated = datetime.now()
            asset_data["portfolio"]["assets"][i] = updated_asset.dict()
            update_total_value()
            logger.info(f"자산 업데이트됨: {asset_id}")
            return updated_asset
    
    raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")

@router.delete("/assets/{asset_id}", tags=["Assets"])
async def delete_asset(asset_id: str):
    """자산 삭제"""
    for i, asset in enumerate(asset_data["portfolio"]["assets"]):
        if asset["id"] == asset_id:
            deleted_asset = asset_data["portfolio"]["assets"].pop(i)
            update_total_value()
            logger.info(f"자산 삭제됨: {asset_id}")
            return {"message": f"자산 {asset_id}가 삭제되었습니다", "deleted_asset": deleted_asset}
    
    raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")

@router.post("/sync", tags=["Sync"])
async def sync_asset_prices(background_tasks: BackgroundTasks):
    """자산 가격 동기화 (백그라운드 작업)"""
    background_tasks.add_task(perform_price_sync)
    return {"message": "자산 가격 동기화가 시작되었습니다"}

@router.get("/health", tags=["Health"])
async def health_check():
    """Asset Manager 헬스 체크"""
    return {
        "status": "healthy",
        "service": "asset-manager",
        "total_assets": len(asset_data["portfolio"]["assets"]),
        "total_value": asset_data["portfolio"]["total_value"],
        "last_sync": asset_data["portfolio"]["last_sync"]
    }

@router.get("/reports/monthly", tags=["Reports"])
async def get_monthly_reports():
    """월간 보고서 목록 조회"""
    try:
        reports_dir = os.path.join(os.path.dirname(__file__), "reports")
        if not os.path.exists(reports_dir):
            return {"reports": [], "message": "아직 생성된 월간 보고서가 없습니다"}
        
        report_files = [f for f in os.listdir(reports_dir) if f.startswith("monthly_report_") and f.endswith(".json")]
        report_files.sort(reverse=True)  # 최신순 정렬
        
        reports = []
        for filename in report_files:
            filepath = os.path.join(reports_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    reports.append({
                        "filename": filename,
                        "report_date": report_data.get("report_date"),
                        "total_value": report_data.get("summary", {}).get("total_value", 0),
                        "total_assets": report_data.get("summary", {}).get("total_assets", 0)
                    })
            except Exception as e:
                logger.error(f"보고서 파일 읽기 오류 ({filename}): {e}")
        
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"월간 보고서 조회 오류: {e}")

@router.get("/reports/monthly/{year}/{month}", tags=["Reports"])
async def get_monthly_report(year: int, month: int):
    """특정 월의 상세 보고서 조회"""
    try:
        filename = f"monthly_report_{year}_{month:02d}.json"
        filepath = os.path.join(os.path.dirname(__file__), "reports", filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"{year}년 {month}월 보고서를 찾을 수 없습니다")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        return report_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 조회 오류: {e}")

@router.post("/reports/generate-monthly", tags=["Reports"])
async def generate_monthly_report_now(background_tasks: BackgroundTasks):
    """현재 시점의 월간 보고서 즉시 생성"""
    background_tasks.add_task(generate_current_monthly_report)
    return {"message": "월간 보고서 생성이 시작되었습니다"}

# 헬퍼 함수들
def update_total_value():
    """포트폴리오 총 가치 계산"""
    total = sum(asset["value"] for asset in asset_data["portfolio"]["assets"])
    asset_data["portfolio"]["total_value"] = total
    asset_data["portfolio"]["last_sync"] = datetime.now()

async def perform_price_sync():
    """실제 가격 동기화 작업 (모의)"""
    logger.info("자산 가격 동기화 시작...")
    
    # 실제로는 외부 API를 호출하여 가격 정보를 가져옴
    for asset in asset_data["portfolio"]["assets"]:
        if asset["type"] in ["stock", "crypto"]:
            # 모의 가격 변동 (±5%)
            import random
            change_rate = random.uniform(-0.05, 0.05)
            asset["value"] *= (1 + change_rate)
            asset["last_updated"] = datetime.now().isoformat()
            logger.info(f"{asset['name']} 가격 업데이트: {asset['value']:.2f}")
    
    update_total_value()
    logger.info("자산 가격 동기화 완료")

# 백그라운드 태스크들
async def background_price_monitor():
    """백그라운드 가격 모니터링"""
    while True:
        try:
            await perform_price_sync()
            # 30분마다 실행
            await asyncio.sleep(1800)
        except Exception as e:
            logger.error(f"백그라운드 가격 모니터링 오류: {e}")
            await asyncio.sleep(60)  # 오류 시 1분 후 재시도

async def monthly_portfolio_report():
    """매월 1일 포트폴리오 월간 보고서 생성"""
    while True:
        try:
            now = datetime.now()
            
            # 다음 달 1일 계산
            if now.month == 12:
                next_month_first = datetime(now.year + 1, 1, 1, 9, 0, 0)  # 다음년 1월 1일 오전 9시
            else:
                next_month_first = datetime(now.year, now.month + 1, 1, 9, 0, 0)  # 다음달 1일 오전 9시
            
            # 다음 실행까지 대기 시간 계산
            time_until_next = (next_month_first - now).total_seconds()
            
            if time_until_next > 0:
                logger.info(f"월간 보고서 다음 실행 예정: {next_month_first.strftime('%Y-%m-%d %H:%M:%S')}")
                await asyncio.sleep(time_until_next)
            
            # 매월 1일 오전 9시에 실행
            logger.info("=== 월간 포트폴리오 보고서 생성 시작 ===")
            
            # 월간 통계 계산
            portfolio = asset_data["portfolio"]
            total_assets = len(portfolio["assets"])
            total_value = portfolio["total_value"]
            
            # 자산 유형별 분석
            asset_by_type = {}
            for asset in portfolio["assets"]:
                asset_type = asset["type"]
                if asset_type not in asset_by_type:
                    asset_by_type[asset_type] = {"count": 0, "total_value": 0}
                asset_by_type[asset_type]["count"] += 1
                asset_by_type[asset_type]["total_value"] += asset["value"]
            
            # 보고서 데이터 생성
            report_data = {
                "report_date": now.strftime('%Y-%m-%d'),
                "report_type": "monthly_portfolio",
                "summary": {
                    "total_assets": total_assets,
                    "total_value": total_value,
                    "currency": "KRW"
                },
                "asset_breakdown": asset_by_type,
                "top_assets": sorted(
                    portfolio["assets"], 
                    key=lambda x: x["value"], 
                    reverse=True
                )[:5]  # 상위 5개 자산
            }
            
            # 보고서 파일 저장
            report_filename = f"monthly_report_{now.strftime('%Y_%m')}.json"
            report_path = os.path.join(os.path.dirname(__file__), "reports", report_filename)
            
            # reports 디렉토리 생성
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"월간 보고서 생성 완료: {report_filename}")
            logger.info(f"총 자산: {total_assets}개, 총 가치: {total_value:,.0f} KRW")
            
            # 다음 달까지 대기하는 대신 1시간 후 다시 체크 (안전장치)
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"월간 보고서 생성 오류: {e}")
            await asyncio.sleep(3600)  # 오류 시 1시간 후 재시도

async def portfolio_backup():
    """포트폴리오 데이터 백업"""
    while True:
        try:
            # 1시간마다 데이터 백업
            backup_file = f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = os.path.join(os.path.dirname(__file__), "backups", backup_file)
            
            # backups 디렉토리 생성
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(asset_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"포트폴리오 백업 완료: {backup_file}")
            await asyncio.sleep(3600)  # 1시간
        except Exception as e:
            logger.error(f"포트폴리오 백업 오류: {e}")
            await asyncio.sleep(600)  # 오류 시 10분 후 재시도

async def generate_current_monthly_report():
    """현재 시점의 월간 보고서 즉시 생성"""
    try:
        now = datetime.now()
        logger.info("=== 수동 월간 포트폴리오 보고서 생성 시작 ===")
        
        # 월간 통계 계산
        portfolio = asset_data["portfolio"]
        total_assets = len(portfolio["assets"])
        total_value = portfolio["total_value"]
        
        # 자산 유형별 분석
        asset_by_type = {}
        for asset in portfolio["assets"]:
            asset_type = asset["type"]
            if asset_type not in asset_by_type:
                asset_by_type[asset_type] = {"count": 0, "total_value": 0}
            asset_by_type[asset_type]["count"] += 1
            asset_by_type[asset_type]["total_value"] += asset["value"]
        
        # 보고서 데이터 생성
        report_data = {
            "report_date": now.strftime('%Y-%m-%d'),
            "report_type": "monthly_portfolio_manual",
            "generated_at": now.isoformat(),
            "summary": {
                "total_assets": total_assets,
                "total_value": total_value,
                "currency": "KRW"
            },
            "asset_breakdown": asset_by_type,
            "top_assets": sorted(
                portfolio["assets"], 
                key=lambda x: x["value"], 
                reverse=True
            )[:5]  # 상위 5개 자산
        }
        
        # 보고서 파일 저장
        report_filename = f"monthly_report_manual_{now.strftime('%Y_%m_%d_%H%M%S')}.json"
        report_path = os.path.join(os.path.dirname(__file__), "reports", report_filename)
        
        # reports 디렉토리 생성
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"수동 월간 보고서 생성 완료: {report_filename}")
        logger.info(f"총 자산: {total_assets}개, 총 가치: {total_value:,.0f} KRW")
        
    except Exception as e:
        logger.error(f"수동 월간 보고서 생성 오류: {e}")

# 모듈 인터페이스 함수들
def get_router():
    """라우터 반환"""
    return router

async def start_background_tasks():
    """백그라운드 태스크 시작"""
    logger.info("Asset Manager 백그라운드 태스크 시작")
    
    # 백그라운드 태스크들을 비동기로 실행
    tasks = [
        background_price_monitor(),
        portfolio_backup(),
        monthly_portfolio_report()  # 월간 보고서 태스크 추가
    ]
    
    # 태스크들을 동시에 실행하되 오류가 발생해도 다른 태스크는 계속 실행
    await asyncio.gather(*tasks, return_exceptions=True)

# 초기 데이터 로드
def load_initial_data():
    """초기 데이터 로드 (예제)"""
    initial_assets = [
        {
            "id": "asset_1",
            "name": "삼성전자",
            "type": "stock",
            "value": 1000000,
            "currency": "KRW",
            "last_updated": datetime.now().isoformat()
        },
        {
            "id": "asset_2", 
            "name": "Bitcoin",
            "type": "crypto",
            "value": 50000000,
            "currency": "KRW",
            "last_updated": datetime.now().isoformat()
        }
    ]
    
    asset_data["portfolio"]["assets"] = initial_assets
    update_total_value()
    logger.info("초기 자산 데이터 로드 완료")

# 모듈 초기화
load_initial_data()