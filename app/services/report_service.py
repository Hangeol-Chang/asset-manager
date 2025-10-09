"""
보고서 관리 서비스
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict
from services.asset_service import asset_service

logger = logging.getLogger("report-service")

class ReportService:
    """보고서 관리 서비스"""
    
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_monthly_report(self, manual: bool = False) -> str:
        """월간 보고서 생성"""
        try:
            now = datetime.now()
            report_type = "monthly_portfolio_manual" if manual else "monthly_portfolio"
            
            logger.info(f"=== {'수동' if manual else '자동'} 월간 포트폴리오 보고서 생성 시작 ===")
            
            # 보고서 데이터 생성
            report_data = asset_service.get_monthly_report_data()
            report_data["report_type"] = report_type
            
            # 보고서 파일명 생성
            if manual:
                filename = f"monthly_report_manual_{now.strftime('%Y_%m_%d_%H%M%S')}.json"
            else:
                filename = f"monthly_report_{now.strftime('%Y_%m')}.json"
            
            filepath = os.path.join(self.reports_dir, filename)
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"월간 보고서 생성 완료: {filename}")
            logger.info(f"총 자산: {report_data['summary']['total_assets']}개, "
                       f"총 가치: {report_data['summary']['total_value']:,.0f} KRW")
            
            return filename
            
        except Exception as e:
            logger.error(f"월간 보고서 생성 오류: {e}")
            raise
    
    def get_monthly_reports(self) -> Dict:
        """월간 보고서 목록 조회"""
        try:
            if not os.path.exists(self.reports_dir):
                return {"reports": [], "message": "아직 생성된 월간 보고서가 없습니다"}
            
            report_files = [
                f for f in os.listdir(self.reports_dir) 
                if f.startswith("monthly_report_") and f.endswith(".json")
            ]
            report_files.sort(reverse=True)  # 최신순 정렬
            
            reports = []
            for filename in report_files:
                filepath = os.path.join(self.reports_dir, filename)
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
            raise Exception(f"월간 보고서 조회 오류: {e}")
    
    def get_monthly_report(self, year: int, month: int) -> Dict:
        """특정 월의 상세 보고서 조회"""
        try:
            filename = f"monthly_report_{year}_{month:02d}.json"
            filepath = os.path.join(self.reports_dir, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"{year}년 {month}월 보고서를 찾을 수 없습니다")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"보고서 조회 오류: {e}")

# 전역 보고서 서비스 인스턴스
report_service = ReportService()