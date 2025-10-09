from fastapi import FastAPI
import uvicorn
from router import router

# 독립 실행용 FastAPI 앱
app = FastAPI(
    title="Asset Manager",
    description="자산 관리 및 가계부 API",
    version="1.0.0"
)

# 라우터 등록
app.include_router(router, prefix="/asset-manager")

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "Asset Manager API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )