"""
Asset Manager 데이터 저장소
"""

from datetime import datetime
from typing import Dict, List, Optional
from models.asset_models import Asset

class AssetDataStore:
    """자산 데이터 저장소 클래스"""
    
    def __init__(self):
        self.data = {
            "portfolio": {
                "total_value": 0.0,
                "assets": [],
                "last_sync": datetime.now()
            }
        }
        self.load_initial_data()
    
    def get_portfolio(self) -> Dict:
        """포트폴리오 조회"""
        return self.data["portfolio"]
    
    def get_assets(self) -> List[Dict]:
        """모든 자산 조회"""
        return self.data["portfolio"]["assets"]
    
    def add_asset(self, asset: Asset) -> Asset:
        """자산 추가"""
        asset.id = f"asset_{len(self.data['portfolio']['assets']) + 1}"
        asset.last_updated = datetime.now()
        
        asset_dict = asset.dict()
        self.data["portfolio"]["assets"].append(asset_dict)
        self.update_total_value()
        
        return asset
    
    def update_asset(self, asset_id: str, updated_asset: Asset) -> Optional[Asset]:
        """자산 업데이트"""
        for i, asset in enumerate(self.data["portfolio"]["assets"]):
            if asset["id"] == asset_id:
                updated_asset.id = asset_id
                updated_asset.last_updated = datetime.now()
                self.data["portfolio"]["assets"][i] = updated_asset.dict()
                self.update_total_value()
                return updated_asset
        return None
    
    def delete_asset(self, asset_id: str) -> Optional[Dict]:
        """자산 삭제"""
        for i, asset in enumerate(self.data["portfolio"]["assets"]):
            if asset["id"] == asset_id:
                deleted_asset = self.data["portfolio"]["assets"].pop(i)
                self.update_total_value()
                return deleted_asset
        return None
    
    def find_asset_by_id(self, asset_id: str) -> Optional[Dict]:
        """ID로 자산 찾기"""
        for asset in self.data["portfolio"]["assets"]:
            if asset["id"] == asset_id:
                return asset
        return None
    
    def update_total_value(self):
        """포트폴리오 총 가치 계산"""
        total = sum(asset["value"] for asset in self.data["portfolio"]["assets"])
        self.data["portfolio"]["total_value"] = total
        self.data["portfolio"]["last_sync"] = datetime.now()
    
    def get_asset_breakdown(self) -> Dict:
        """자산 유형별 분석"""
        asset_by_type = {}
        for asset in self.data["portfolio"]["assets"]:
            asset_type = asset["type"]
            if asset_type not in asset_by_type:
                asset_by_type[asset_type] = {"count": 0, "total_value": 0}
            asset_by_type[asset_type]["count"] += 1
            asset_by_type[asset_type]["total_value"] += asset["value"]
        return asset_by_type
    
    def get_top_assets(self, limit: int = 5) -> List[Dict]:
        """상위 자산 목록"""
        return sorted(
            self.data["portfolio"]["assets"], 
            key=lambda x: x["value"], 
            reverse=True
        )[:limit]
    
    def load_initial_data(self):
        """초기 데이터 로드"""
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
        
        self.data["portfolio"]["assets"] = initial_assets
        self.update_total_value()

# 전역 데이터 저장소 인스턴스
asset_store = AssetDataStore()