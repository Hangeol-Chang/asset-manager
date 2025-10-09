"""
Asset Manager 백그라운드 태스크
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from services.asset_service import asset_service
from services.report_service import report_service

logger = logging.getLogger("asset-tasks")

class AssetBackgroundTasks:
    """자산 관리 백그라운드 태스크 클래스"""
    
    def __init__(self):
        self.backup_dir = os.path.join(os.path.dirname(__file__), "..", "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def price_monitor(self):
        """백그라운드 가격 모니터링"""
        while True:
            try:
                await asset_service.sync_asset_prices()
                # 30분마다 실행
                await asyncio.sleep(1800)
            except Exception as e:
                logger.error(f"백그라운드 가격 모니터링 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 후 재시도
    
    async def portfolio_backup(self):
        """포트폴리오 데이터 백업"""
        while True:
            try:
                # 1시간마다 데이터 백업
                backup_file = f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = os.path.join(self.backup_dir, backup_file)
                
                # 포트폴리오 데이터 가져오기
                portfolio_data = asset_service.store.data
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(portfolio_data, f, ensure_ascii=False, indent=2, default=str)
                
                logger.info(f"포트폴리오 백업 완료: {backup_file}")
                await asyncio.sleep(3600)  # 1시간
            except Exception as e:
                logger.error(f"포트폴리오 백업 오류: {e}")
                await asyncio.sleep(600)  # 오류 시 10분 후 재시도
    
    async def monthly_report_scheduler(self):
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
                report_service.generate_monthly_report(manual=False)
                
                # 다음 달까지 대기하는 대신 1시간 후 다시 체크 (안전장치)
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"월간 보고서 생성 오류: {e}")
                await asyncio.sleep(3600)  # 오류 시 1시간 후 재시도
    
    async def start_all_tasks(self):
        """모든 백그라운드 태스크 시작"""
        logger.info("Asset Manager 백그라운드 태스크 시작")
        
        # 백그라운드 태스크들을 비동기로 실행
        tasks = [
            self.price_monitor(),
            self.portfolio_backup(),
            self.monthly_report_scheduler()
        ]
        
        # 태스크들을 동시에 실행하되 오류가 발생해도 다른 태스크는 계속 실행
        await asyncio.gather(*tasks, return_exceptions=True)

# 전역 백그라운드 태스크 인스턴스
background_tasks = AssetBackgroundTasks()