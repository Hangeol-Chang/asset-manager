"""
Asset Manager 비즈니스 로직 서비스
"""

import logging
import random
from datetime import datetime
from models.asset_models import Asset, AssetPortfolio
from services.data_store import asset_store

logger = logging.getLogger("asset-service")

class AssetService:
    """자산 관리 서비스"""
    
    def __init__(self):
        self.store = asset_store
    
    def get_portfolio(self) -> AssetPortfolio:
        """포트폴리오 조회"""
        portfolio = self.store.get_portfolio()
        return AssetPortfolio(
            total_value=portfolio["total_value"],
            assets=[Asset(**asset) for asset in portfolio["assets"]],
            last_sync=portfolio["last_sync"]
        )
    
    def get_all_assets(self) -> list[Asset]:
        """모든 자산 목록 조회"""
        return [Asset(**asset) for asset in self.store.get_assets()]
    
    def create_asset(self, asset: Asset) -> Asset:
        """새 자산 생성"""
        created_asset = self.store.add_asset(asset)
        logger.info(f"새 자산 추가됨: {asset.name} - {asset.value} {asset.currency}")
        return created_asset
    
    def update_asset(self, asset_id: str, updated_asset: Asset) -> Asset:
        """자산 업데이트"""
        result = self.store.update_asset(asset_id, updated_asset)
        if result:
            logger.info(f"자산 업데이트됨: {asset_id}")
            return result
        else:
            raise ValueError("자산을 찾을 수 없습니다")
    
    def delete_asset(self, asset_id: str) -> dict:
        """자산 삭제"""
        deleted_asset = self.store.delete_asset(asset_id)
        if deleted_asset:
            logger.info(f"자산 삭제됨: {asset_id}")
            return {"message": f"자산 {asset_id}가 삭제되었습니다", "deleted_asset": deleted_asset}
        else:
            raise ValueError("자산을 찾을 수 없습니다")
    
    async def sync_asset_prices(self):
        """자산 가격 동기화"""
        logger.info("자산 가격 동기화 시작...")
        
        # 실제로는 외부 API를 호출하여 가격 정보를 가져옴
        for asset in self.store.get_assets():
            if asset["type"] in ["stock", "crypto"]:
                # 모의 가격 변동 (±5%)
                change_rate = random.uniform(-0.05, 0.05)
                asset["value"] *= (1 + change_rate)
                asset["last_updated"] = datetime.now().isoformat()
                logger.info(f"{asset['name']} 가격 업데이트: {asset['value']:.2f}")
        
        self.store.update_total_value()
        logger.info("자산 가격 동기화 완료")
    
    def get_monthly_report_data(self) -> dict:
        """월간 보고서 데이터 생성"""
        portfolio = self.store.get_portfolio()
        total_assets = len(portfolio["assets"])
        total_value = portfolio["total_value"]
        
        return {
            "report_date": datetime.now().strftime('%Y-%m-%d'),
            "report_type": "monthly_portfolio",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_assets": total_assets,
                "total_value": total_value,
                "currency": "KRW"
            },
            "asset_breakdown": self.store.get_asset_breakdown(),
            "top_assets": self.store.get_top_assets()
        }
    
    def get_health_status(self) -> dict:
        """헬스 상태 조회"""
        portfolio = self.store.get_portfolio()
        return {
            "status": "healthy",
            "service": "asset-manager",
            "total_assets": len(portfolio["assets"]),
            "total_value": portfolio["total_value"],
            "last_sync": portfolio["last_sync"]
        }

# 전역 서비스 인스턴스
asset_service = AssetService()