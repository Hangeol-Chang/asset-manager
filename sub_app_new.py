"""
Asset Manager Sub Application

자산 관리 모듈 - 가계부, 자산 추적, 지출 분석 등의 기능을 제공합니다.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template

# 현재 모듈의 경로를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Flask 서브 앱 생성 - 템플릿과 static 폴더 설정
sub_app = Flask(__name__, 
                template_folder=os.path.join(current_dir, 'web', 'templates'),
                static_folder=os.path.join(current_dir, 'web', 'static'),
                static_url_path='/asset-manager/static')

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
    # 실제 데이터 로드
    assets = load_json_file(ASSETS_FILE)
    transactions = load_json_file(TRANSACTIONS_FILE)
    categories = load_json_file(CATEGORIES_FILE)
    
    # 총 자산 계산
    total_assets = 0
    if 'cash' in assets:
        total_assets += assets['cash'].get('amount', 0)
    
    for account in assets.get('bank_accounts', []):
        total_assets += account.get('amount', 0)
    
    for investment in assets.get('investments', []):
        total_assets += investment.get('amount', 0)
    
    # 최근 거래 내역 (최근 5개)
    recent_transactions = sorted(transactions, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    # 이번 달 수입/지출 계산
    current_month = datetime.now().strftime('%Y-%m')
    monthly_income = sum(t['amount'] for t in transactions if t['date'].startswith(current_month) and t['type'] == 'income')
    monthly_expense = sum(t['amount'] for t in transactions if t['date'].startswith(current_month) and t['type'] == 'expense')
    monthly_balance = monthly_income - monthly_expense
    
    return render_template('dashboard.html',
                         total_assets=total_assets,
                         monthly_income=monthly_income,
                         monthly_expense=monthly_expense,
                         monthly_balance=monthly_balance,
                         current_date=datetime.now().strftime('%Y년 %m월 %d일'),
                         recent_transactions=recent_transactions,
                         categories=categories)

# 거래 내역 관련 API
@sub_app.route('/transactions', methods=['GET'])
def get_transactions():
    """거래 내역 조회 - 웹 페이지 또는 JSON 응답"""
    transactions = load_json_file(TRANSACTIONS_FILE)
    
    # 필터링 파라미터 받기
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    transaction_type = request.args.get('type')
    
    # 필터링 적용
    filtered_transactions = transactions.copy()
    
    if start_date:
        filtered_transactions = [t for t in filtered_transactions if t['date'] >= start_date]
    
    if end_date:
        filtered_transactions = [t for t in filtered_transactions if t['date'] <= end_date]
    
    if category:
        filtered_transactions = [t for t in filtered_transactions if t['category'] == category]
    
    if transaction_type:
        filtered_transactions = [t for t in filtered_transactions if t['type'] == transaction_type]
    
    # 날짜순 정렬 (최신순)
    filtered_transactions = sorted(filtered_transactions, key=lambda x: x.get('created_at', ''), reverse=True)
    
    # JSON 요청인 경우 API 응답
    if request.headers.get('Content-Type') == 'application/json' or request.is_json:
        return jsonify({
            'status': 'success',
            'transactions': filtered_transactions,
            'total_count': len(filtered_transactions)
        })
    
    # 웹 페이지 요청인 경우 HTML 응답
    categories = load_json_file(CATEGORIES_FILE)
    
    # 통계 계산
    total_income = sum(t['amount'] for t in filtered_transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in filtered_transactions if t['type'] == 'expense')
    net_amount = total_income - total_expense
    
    return render_template('transactions.html',
                         filtered_transactions=filtered_transactions,
                         categories=categories,
                         total_income=total_income,
                         total_expense=total_expense,
                         net_amount=net_amount,
                         request=request)

@sub_app.route('/transactions', methods=['POST'])
def add_transaction():
    """거래 내역 추가"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['amount', 'category', 'type', 'description', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        # 새 거래 내역 생성
        new_transaction = {
            'id': str(int(datetime.now().timestamp() * 1000)),  # 고유 ID 생성
            'amount': data['amount'],
            'category': data['category'],
            'type': data['type'],  # 'income' 또는 'expense'
            'description': data['description'],
            'date': data['date'],
            'created_at': datetime.now().isoformat()
        }
        
        # 기존 거래 내역 로드
        transactions = load_json_file(TRANSACTIONS_FILE)
        
        # 새 거래 내역 추가
        transactions.append(new_transaction)
        
        # 파일에 저장
        if save_json_file(TRANSACTIONS_FILE, transactions):
            return jsonify({'status': 'success', 'transaction': new_transaction})
        else:
            return jsonify({'status': 'error', 'message': '파일 저장 중 오류가 발생했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"Error adding transaction: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 자산 관리 API
@sub_app.route('/assets', methods=['GET'])
def get_assets():
    """자산 현황 조회 - 웹 페이지 또는 JSON 응답"""
    assets = load_json_file(ASSETS_FILE)
    
    # 총 자산 계산
    total_assets = 0
    if 'cash' in assets:
        total_assets += assets['cash'].get('amount', 0)
    
    for account in assets.get('bank_accounts', []):
        total_assets += account.get('amount', 0)
    
    for investment in assets.get('investments', []):
        total_assets += investment.get('amount', 0)
    
    # JSON 요청인 경우 API 응답
    if request.headers.get('Content-Type') == 'application/json' or request.is_json:
        return jsonify({
            'status': 'success',
            'assets': assets,
            'total_assets': total_assets
        })
    
    # 웹 페이지 요청인 경우 HTML 응답
    return render_template('assets.html',
                         assets=assets,
                         total_assets=total_assets)

# 분석 API
@sub_app.route('/analysis', methods=['GET'])
def get_analysis():
    """지출 분석 데이터"""
    transactions = load_json_file(TRANSACTIONS_FILE)
    
    # 기본 분석 데이터 (향후 확장 가능)
    analysis_data = {
        'monthly_trends': {},
        'category_breakdown': {},
        'income_vs_expense': {}
    }
    
    # JSON 응답
    return jsonify({
        'status': 'success',
        'analysis': analysis_data
    })

# 카테고리 API
@sub_app.route('/categories', methods=['GET'])
def get_categories():
    """카테고리 목록 조회"""
    categories = load_json_file(CATEGORIES_FILE)
    return jsonify({
        'status': 'success',
        'categories': categories
    })

# 앱 시작 시 데이터 디렉토리 확인
ensure_data_directory()

if __name__ == '__main__':
    sub_app.run(debug=True, port=5001)
