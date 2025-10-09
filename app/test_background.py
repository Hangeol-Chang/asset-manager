#!/usr/bin/env python3
"""
Asset Manager 백그라운드 태스크 테스트 스크립트
월간 보고서 생성 기능을 테스트합니다.
"""

import asyncio
import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# sub_main 모듈 import
from sub_main import generate_current_monthly_report, asset_data, logger

async def test_monthly_report():
    """월간 보고서 생성 테스트"""
    print("=== Asset Manager 백그라운드 태스크 테스트 ===")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 현재 자산 데이터 확인
    portfolio = asset_data["portfolio"]
    print(f"현재 자산 수: {len(portfolio['assets'])}개")
    print(f"총 자산 가치: {portfolio['total_value']:,.0f} KRW")
    
    print("\n자산 목록:")
    for i, asset in enumerate(portfolio["assets"], 1):
        print(f"  {i}. {asset['name']} ({asset['type']}): {asset['value']:,.0f} {asset['currency']}")
    
    # 월간 보고서 생성 테스트
    print("\n=== 월간 보고서 생성 테스트 ===")
    try:
        await generate_current_monthly_report()
        print("✅ 월간 보고서 생성 성공!")
        
        # 생성된 보고서 파일 확인
        reports_dir = os.path.join(current_dir, "reports")
        if os.path.exists(reports_dir):
            report_files = [f for f in os.listdir(reports_dir) if f.startswith("monthly_report_")]
            print(f"\n생성된 보고서 파일 수: {len(report_files)}개")
            
            # 최신 보고서 파일 내용 표시
            if report_files:
                latest_report = max(report_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
                print(f"최신 보고서: {latest_report}")
                
                # 보고서 내용 간단히 표시
                import json
                with open(os.path.join(reports_dir, latest_report), 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                print(f"보고서 날짜: {report_data.get('report_date')}")
                print(f"보고서 유형: {report_data.get('report_type')}")
                summary = report_data.get('summary', {})
                print(f"요약 정보:")
                print(f"  - 총 자산: {summary.get('total_assets')}개")
                print(f"  - 총 가치: {summary.get('total_value'):,.0f} {summary.get('currency')}")
                
                asset_breakdown = report_data.get('asset_breakdown', {})
                if asset_breakdown:
                    print(f"자산 유형별 분석:")
                    for asset_type, data in asset_breakdown.items():
                        print(f"  - {asset_type}: {data['count']}개, {data['total_value']:,.0f} KRW")
        
    except Exception as e:
        print(f"❌ 월간 보고서 생성 실패: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # 비동기 테스트 실행
    asyncio.run(test_monthly_report())