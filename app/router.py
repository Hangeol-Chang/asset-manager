from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uuid

router = APIRouter()

# 데이터 모델
class Transaction(BaseModel):
    id: Optional[str] = None
    amount: float
    category: str
    description: str
    date: date
    type: str  # "income" or "expense"
    
class Asset(BaseModel):
    id: Optional[str] = None
    name: str
    type: str  # "cash", "bank", "investment", "real_estate"
    amount: float
    currency: str = "KRW"

class Category(BaseModel):
    id: Optional[str] = None
    name: str
    type: str  # "income" or "expense"
    color: str = "#4f46e5"

# 메모리 저장소 (실제로는 데이터베이스 사용)
transactions_db = []
assets_db = []
categories_db = [
    {"id": "1", "name": "급여", "type": "income", "color": "#10b981"},
    {"id": "2", "name": "식비", "type": "expense", "color": "#ef4444"},
    {"id": "3", "name": "교통비", "type": "expense", "color": "#f59e0b"},
    {"id": "4", "name": "쇼핑", "type": "expense", "color": "#8b5cf6"},
]

# 거래 내역 API
@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(limit: int = 50, offset: int = 0):
    """거래 내역 조회"""
    return transactions_db[offset:offset + limit]

@router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: Transaction):
    """거래 내역 생성"""
    transaction.id = str(uuid.uuid4())
    transactions_db.append(transaction.dict())
    return transaction

@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction: Transaction):
    """거래 내역 수정"""
    for i, tx in enumerate(transactions_db):
        if tx["id"] == transaction_id:
            transaction.id = transaction_id
            transactions_db[i] = transaction.dict()
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """거래 내역 삭제"""
    for i, tx in enumerate(transactions_db):
        if tx["id"] == transaction_id:
            del transactions_db[i]
            return {"message": "Transaction deleted"}
    raise HTTPException(status_code=404, detail="Transaction not found")

# 자산 API
@router.get("/assets", response_model=List[Asset])
async def get_assets():
    """자산 목록 조회"""
    return assets_db

@router.post("/assets", response_model=Asset)
async def create_asset(asset: Asset):
    """자산 생성"""
    asset.id = str(uuid.uuid4())
    assets_db.append(asset.dict())
    return asset

@router.put("/assets/{asset_id}", response_model=Asset)
async def update_asset(asset_id: str, asset: Asset):
    """자산 수정"""
    for i, a in enumerate(assets_db):
        if a["id"] == asset_id:
            asset.id = asset_id
            assets_db[i] = asset.dict()
            return asset
    raise HTTPException(status_code=404, detail="Asset not found")

@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """자산 삭제"""
    for i, a in enumerate(assets_db):
        if a["id"] == asset_id:
            del assets_db[i]
            return {"message": "Asset deleted"}
    raise HTTPException(status_code=404, detail="Asset not found")

# 카테고리 API
@router.get("/categories", response_model=List[Category])
async def get_categories():
    """카테고리 목록 조회"""
    return categories_db

@router.post("/categories", response_model=Category)
async def create_category(category: Category):
    """카테고리 생성"""
    category.id = str(uuid.uuid4())
    categories_db.append(category.dict())
    return category

# 통계 API
@router.get("/stats/summary")
async def get_summary():
    """요약 통계"""
    total_income = sum(tx["amount"] for tx in transactions_db if tx["type"] == "income")
    total_expense = sum(tx["amount"] for tx in transactions_db if tx["type"] == "expense")
    total_assets = sum(asset["amount"] for asset in assets_db)
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_income": total_income - total_expense,
        "total_assets": total_assets,
        "transaction_count": len(transactions_db)
    }

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "module": "asset-manager",
        "transactions": len(transactions_db),
        "assets": len(assets_db),
        "categories": len(categories_db)
    }