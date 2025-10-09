"""
Asset Manager 데이터 모델
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Asset(BaseModel):
    """자산 모델"""
    id: Optional[str] = None
    name: str
    type: str  # 'stock', 'crypto', 'real_estate', 'cash', etc.
    value: float
    currency: str = "KRW"
    last_updated: Optional[datetime] = None

class AssetPortfolio(BaseModel):
    """포트폴리오 모델"""
    total_value: float
    assets: List[Asset]
    last_sync: datetime

class AssetTypeBreakdown(BaseModel):
    """자산 유형별 분석"""
    count: int
    total_value: float

class MonthlyReport(BaseModel):
    """월간 보고서 모델"""
    report_date: str
    report_type: str
    generated_at: Optional[str] = None
    summary: dict
    asset_breakdown: dict
    top_assets: List[Asset]