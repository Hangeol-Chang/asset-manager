"""
Asset Manager Sub Application

자산 관리 모듈 - 가계부, 자산 추적, 지출 분석 등의 기능을 제공합니다.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string

# 현재 모듈의 경로를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Flask 서브 앱 생성
sub_app = Flask(__name__)

# 로깅 설정
logger = logging.getLogger('asset-manager')

# 데이터 파일 경로
DATA_DIR = os.path.join(current_dir, 'data')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')
CATEGORIES_FILE = os.path.join(DATA_DIR, 'categories.json')
ASSETS_FILE = os.path.join(DATA_DIR, 'assets.json')

def ensure_data_directory():
    """데이터 디렉토리 및 기본 파일들 생성"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # 기본 카테고리 파일 생성
    if not os.path.exists(CATEGORIES_FILE):
        default_categories = {
            "income": ["급여", "부업", "투자수익", "기타수입"],
            "expense": ["식비", "교통비", "주거비", "의료비", "쇼핑", "여가", "교육", "기타지출"]
        }
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_categories, f, ensure_ascii=False, indent=2)
    
    # 기본 거래 내역 파일 생성
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 기본 자산 파일 생성
    if not os.path.exists(ASSETS_FILE):
        default_assets = {
            "cash": {"name": "현금", "amount": 0, "currency": "KRW"},
            "bank_accounts": [],
            "investments": [],
            "real_estate": [],
            "other": []
        }
        with open(ASSETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_assets, f, ensure_ascii=False, indent=2)

def load_json_file(filepath):
    """JSON 파일 로드"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {filepath}")
        return []

def save_json_file(filepath, data):
    """JSON 파일 저장"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save file {filepath}: {e}")
        return False

# 메인 대시보드
@sub_app.route('/')
def dashboard():
    """자산 관리 대시보드"""
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Asset Manager - 자산 관리</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                text-align: center;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .card h3 {
                margin-top: 0;
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }
            .api-links {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 15px;
            }
            .api-link {
                padding: 8px 12px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
            }
            .api-link:hover {
                background: #0056b3;
                color: white;
                text-decoration: none;
            }
            .summary-item {
                margin: 10px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #28a745;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💰 Asset Manager</h1>
            <p>개인 자산 및 가계부 관리 시스템</p>
        </div>
        
        <div class="cards">
            <div class="card">
                <h3>📊 거래 내역 관리</h3>
                <p>수입과 지출을 기록하고 관리합니다.</p>
                <div class="api-links">
                    <a href="/asset-manager/transactions" class="api-link">거래 내역 조회</a>
                    <a href="/asset-manager/add-transaction" class="api-link">거래 추가</a>
                </div>
            </div>
            
            <div class="card">
                <h3>💼 자산 관리</h3>
                <p>현금, 예금, 투자 등 전체 자산을 관리합니다.</p>
                <div class="api-links">
                    <a href="/asset-manager/assets" class="api-link">자산 현황</a>
                    <a href="/asset-manager/add-asset" class="api-link">자산 추가</a>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 분석 및 통계</h3>
                <p>지출 패턴 분석과 월별 통계를 확인합니다.</p>
                <div class="api-links">
                    <a href="/asset-manager/analysis" class="api-link">지출 분석</a>
                    <a href="/asset-manager/monthly-report" class="api-link">월별 리포트</a>
                </div>
            </div>
            
            <div class="card">
                <h3>⚙️ 설정</h3>
                <p>카테고리 및 기타 설정을 관리합니다.</p>
                <div class="api-links">
                    <a href="/asset-manager/categories" class="api-link">카테고리 관리</a>
                    <a href="/asset-manager/export" class="api-link">데이터 내보내기</a>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📋 API 엔드포인트</h3>
            <div class="summary-item">
                <strong>GET /asset-manager/</strong> - 대시보드
            </div>
            <div class="summary-item">
                <strong>GET /asset-manager/transactions</strong> - 거래 내역 조회
            </div>
            <div class="summary-item">
                <strong>POST /asset-manager/transactions</strong> - 거래 내역 추가
            </div>
            <div class="summary-item">
                <strong>GET /asset-manager/assets</strong> - 자산 현황 조회
            </div>
            <div class="summary-item">
                <strong>GET /asset-manager/analysis</strong> - 지출 분석 데이터
            </div>
        </div>
    </body>
    </html>
    """
    return dashboard_html

# 거래 내역 관련 API
@sub_app.route('/transactions', methods=['GET'])
def get_transactions():
    """거래 내역 조회"""
    transactions = load_json_file(TRANSACTIONS_FILE)
    
    # 쿼리 파라미터로 필터링
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    transaction_type = request.args.get('type')  # income 또는 expense
    
    filtered_transactions = transactions
    
    if start_date:
        filtered_transactions = [t for t in filtered_transactions if t['date'] >= start_date]
    if end_date:
        filtered_transactions = [t for t in filtered_transactions if t['date'] <= end_date]
    if category:
        filtered_transactions = [t for t in filtered_transactions if t['category'] == category]
    if transaction_type:
        filtered_transactions = [t for t in filtered_transactions if t['type'] == transaction_type]
    
    return jsonify({
        'status': 'success',
        'transactions': filtered_transactions,
        'total_count': len(filtered_transactions)
    })

@sub_app.route('/transactions', methods=['POST'])
def add_transaction():
    """거래 내역 추가"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['amount', 'category', 'type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
        
        # 새 거래 생성
        new_transaction = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'amount': float(data['amount']),
            'category': data['category'],
            'type': data['type'],  # 'income' 또는 'expense'
            'description': data['description'],
            'created_at': datetime.now().isoformat()
        }
        
        # 거래 내역 로드 및 추가
        transactions = load_json_file(TRANSACTIONS_FILE)
        transactions.append(new_transaction)
        
        # 파일 저장
        if save_json_file(TRANSACTIONS_FILE, transactions):
            return jsonify({'status': 'success', 'transaction': new_transaction})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to save transaction'}), 500
            
    except Exception as e:
        logger.error(f"Error adding transaction: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 자산 관리 API
@sub_app.route('/assets', methods=['GET'])
def get_assets():
    """자산 현황 조회"""
    assets = load_json_file(ASSETS_FILE)
    
    # 총 자산 계산
    total_assets = 0
    if 'cash' in assets:
        total_assets += assets['cash'].get('amount', 0)
    
    for account in assets.get('bank_accounts', []):
        total_assets += account.get('amount', 0)
    
    for investment in assets.get('investments', []):
        total_assets += investment.get('amount', 0)
    
    return jsonify({
        'status': 'success',
        'assets': assets,
        'total_assets': total_assets
    })

# 분석 API
@sub_app.route('/analysis', methods=['GET'])
def get_analysis():
    """지출 분석 데이터"""
    transactions = load_json_file(TRANSACTIONS_FILE)
    
    # 월별 수입/지출 분석
    monthly_data = {}
    category_data = {}
    
    for transaction in transactions:
        date = transaction['date']
        month_key = date[:7]  # YYYY-MM
        amount = transaction['amount']
        category = transaction['category']
        trans_type = transaction['type']
        
        # 월별 데이터
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        
        if trans_type == 'income':
            monthly_data[month_key]['income'] += amount
        else:
            monthly_data[month_key]['expense'] += amount
        
        # 카테고리별 데이터
        if category not in category_data:
            category_data[category] = {'income': 0, 'expense': 0}
        
        if trans_type == 'income':
            category_data[category]['income'] += amount
        else:
            category_data[category]['expense'] += amount
    
    return jsonify({
        'status': 'success',
        'monthly_analysis': monthly_data,
        'category_analysis': category_data
    })

# 카테고리 관리 API
@sub_app.route('/categories', methods=['GET'])
def get_categories():
    """카테고리 조회"""
    categories = load_json_file(CATEGORIES_FILE)
    return jsonify({
        'status': 'success',
        'categories': categories
    })

# 헬스 체크
@sub_app.route('/health')
def health():
    """모듈 헬스 체크"""
    return jsonify({
        'status': 'ok',
        'module': 'asset-manager',
        'message': 'Asset Manager is running',
        'features': [
            'Transaction Management',
            'Asset Tracking',
            'Expense Analysis',
            'Category Management'
        ]
    })

def start_background_processes():
    """백그라운드 프로세스 시작 (필요시)"""
    try:
        logger.info("Asset Manager 모듈 초기화 중...")
        
        # 데이터 디렉토리 및 기본 파일 생성
        ensure_data_directory()
        
        logger.info("Asset Manager 모듈 초기화 완료")
        
        # 주기적인 백업이나 분석 작업이 필요한 경우 여기에 추가
        
    except Exception as e:
        logger.error(f"Asset Manager 초기화 오류: {e}")

if __name__ == '__main__':
    # 독립 실행용 (테스트 목적)
    ensure_data_directory()
    sub_app.run(debug=True, port=5001)
