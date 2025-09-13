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
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .header h1 {
                color: #2c3e50;
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            .header p {
                color: #7f8c8d;
                margin: 10px 0 0 0;
                font-size: 1.1em;
            }
            
            /* 자산 현황 카드 */
            .asset-summary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
            }
            .total-assets {
                font-size: 3em;
                font-weight: bold;
                margin: 10px 0;
            }
            .monthly-summary {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-top: 20px;
            }
            .monthly-item {
                background: rgba(255,255,255,0.2);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .monthly-item h4 {
                margin: 0 0 10px 0;
                font-size: 0.9em;
                opacity: 0.9;
            }
            .monthly-item .amount {
                font-size: 1.5em;
                font-weight: bold;
            }
            
            /* 빠른 액션 버튼 */
            .quick-actions {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .action-btn {
                background: white;
                border: 2px solid #ecf0f1;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                color: #2c3e50;
            }
            .action-btn:hover {
                border-color: #667eea;
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
                text-decoration: none;
                color: #667eea;
            }
            .action-btn .icon {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .action-btn .title {
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .action-btn .desc {
                font-size: 0.9em;
                color: #7f8c8d;
            }
            
            /* 최근 거래 내역 */
            .recent-transactions {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
            }
            .recent-transactions h3 {
                margin: 0 0 20px 0;
                color: #2c3e50;
                font-size: 1.3em;
            }
            .transaction-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 0;
                border-bottom: 1px solid #ecf0f1;
            }
            .transaction-item:last-child {
                border-bottom: none;
            }
            .transaction-info {
                flex: 1;
            }
            .transaction-desc {
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            .transaction-meta {
                font-size: 0.9em;
                color: #7f8c8d;
            }
            .transaction-amount {
                font-weight: bold;
                font-size: 1.1em;
            }
            .income {
                color: #27ae60;
            }
            .expense {
                color: #e74c3c;
            }
            
            /* 폼 스타일 */
            .form-container {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                margin-top: 20px;
                display: none;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #2c3e50;
            }
            .form-group input, .form-group select, .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s ease;
            }
            .btn:hover {
                background: #5a6fd8;
            }
            .btn-secondary {
                background: #95a5a6;
                margin-left: 10px;
            }
            .btn-secondary:hover {
                background: #7f8c8d;
            }
            
            @media (max-width: 768px) {
                .monthly-summary {
                    grid-template-columns: 1fr;
                }
                .quick-actions {
                    grid-template-columns: repeat(2, 1fr);
                }
                .total-assets {
                    font-size: 2em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 나의 자산 관리</h1>
                <p>{{ current_date }}</p>
            </div>
            
            <!-- 자산 현황 요약 -->
            <div class="asset-summary">
                <h2>총 자산</h2>
                <div class="total-assets">₩{{ "{:,}".format(total_assets) }}</div>
                <div class="monthly-summary">
                    <div class="monthly-item">
                        <h4>이번 달 수입</h4>
                        <div class="amount">₩{{ "{:,}".format(monthly_income) }}</div>
                    </div>
                    <div class="monthly-item">
                        <h4>이번 달 지출</h4>
                        <div class="amount">₩{{ "{:,}".format(monthly_expense) }}</div>
                    </div>
                    <div class="monthly-item">
                        <h4>이번 달 수지</h4>
                        <div class="amount" style="color: {{ 'lightgreen' if monthly_balance >= 0 else 'lightcoral' }}">
                            ₩{{ "{:,}".format(monthly_balance) }}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 빠른 액션 버튼들 -->
            <div class="quick-actions">
                <a href="#" class="action-btn" onclick="showAddTransaction('expense')">
                    <div class="icon">💸</div>
                    <div class="title">지출 등록</div>
                    <div class="desc">새로운 지출 내역 추가</div>
                </a>
                <a href="#" class="action-btn" onclick="showAddTransaction('income')">
                    <div class="icon">�</div>
                    <div class="title">수입 등록</div>
                    <div class="desc">새로운 수입 내역 추가</div>
                </a>
                <a href="/asset-manager/assets" class="action-btn">
                    <div class="icon">🏦</div>
                    <div class="title">자산 현황</div>
                    <div class="desc">계좌별 잔액 확인</div>
                </a>
                <a href="/asset-manager/analysis" class="action-btn">
                    <div class="icon">📊</div>
                    <div class="title">지출 분석</div>
                    <div class="desc">소비 패턴 분석</div>
                </a>
            </div>
            
            <!-- 거래 내역 추가 폼 -->
            <div id="transaction-form" class="form-container">
                <h3 id="form-title">거래 내역 추가</h3>
                <form id="add-transaction-form">
                    <div class="form-group">
                        <label for="amount">금액 (원)</label>
                        <input type="number" id="amount" name="amount" required>
                    </div>
                    <div class="form-group">
                        <label for="category">카테고리</label>
                        <select id="category" name="category" required>
                            <!-- 카테고리는 JavaScript로 동적 로드 -->
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="description">내용</label>
                        <input type="text" id="description" name="description" required placeholder="예: 점심식사, 급여 등">
                    </div>
                    <div class="form-group">
                        <label for="date">날짜</label>
                        <input type="date" id="date" name="date" required>
                    </div>
                    <input type="hidden" id="type" name="type">
                    <button type="submit" class="btn">등록</button>
                    <button type="button" class="btn btn-secondary" onclick="hideForm()">취소</button>
                </form>
            </div>
            
            <!-- 최근 거래 내역 -->
            <div class="recent-transactions">
                <h3>📋 최근 거래 내역</h3>
                {% if recent_transactions %}
                    {% for transaction in recent_transactions %}
                    <div class="transaction-item">
                        <div class="transaction-info">
                            <div class="transaction-desc">{{ transaction.description }}</div>
                            <div class="transaction-meta">{{ transaction.date }} • {{ transaction.category }}</div>
                        </div>
                        <div class="transaction-amount {{ transaction.type }}">
                            {{ '+' if transaction.type == 'income' else '-' }}₩{{ "{:,}".format(transaction.amount) }}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="text-align: center; color: #7f8c8d; padding: 20px;">아직 거래 내역이 없습니다.</p>
                {% endif %}
                
                {% if recent_transactions|length >= 5 %}
                <div style="text-align: center; margin-top: 20px;">
                    <a href="/asset-manager/transactions" class="btn">전체 거래 내역 보기</a>
                </div>
                {% endif %}
            </div>
        </div>
        
        <script>
            // 오늘 날짜를 기본값으로 설정
            document.getElementById('date').value = new Date().toISOString().split('T')[0];
            
            // 카테고리 데이터
            const categories = {{ categories|tojson }};
            
            function showAddTransaction(type) {
                const form = document.getElementById('transaction-form');
                const title = document.getElementById('form-title');
                const typeInput = document.getElementById('type');
                const categorySelect = document.getElementById('category');
                
                // 폼 제목과 타입 설정
                title.textContent = type === 'income' ? '수입 등록' : '지출 등록';
                typeInput.value = type;
                
                // 카테고리 옵션 설정
                categorySelect.innerHTML = '';
                const categoryList = type === 'income' ? categories.income : categories.expense;
                categoryList.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat;
                    option.textContent = cat;
                    categorySelect.appendChild(option);
                });
                
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth' });
            }
            
            function hideForm() {
                document.getElementById('transaction-form').style.display = 'none';
                document.getElementById('add-transaction-form').reset();
            }
            
            // 폼 제출 처리
            document.getElementById('add-transaction-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {
                    amount: parseFloat(formData.get('amount')),
                    category: formData.get('category'),
                    type: formData.get('type'),
                    description: formData.get('description'),
                    date: formData.get('date')
                };
                
                try {
                    const response = await fetch('/asset-manager/transactions', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('거래 내역이 성공적으로 등록되었습니다!');
                        location.reload(); // 페이지 새로고침으로 최신 데이터 표시
                    } else {
                        alert('오류가 발생했습니다: ' + result.message);
                    }
                } catch (error) {
                    alert('네트워크 오류가 발생했습니다.');
                }
            });
        </script>
    </body>
    </html>
    """
    
    from flask import render_template_string
    return render_template_string(dashboard_html, 
                                total_assets=total_assets,
                                monthly_income=monthly_income,
                                monthly_expense=monthly_expense,
                                monthly_balance=monthly_balance,
                                recent_transactions=recent_transactions,
                                categories=categories,
                                current_date=datetime.now().strftime('%Y년 %m월 %d일'))

# 거래 내역 관련 API
@sub_app.route('/transactions', methods=['GET'])
def get_transactions():
    """거래 내역 조회 - 웹 페이지 또는 JSON 응답"""
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
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #ecf0f1;
            }
            .header h1 {
                color: #2c3e50;
                margin: 0;
                font-size: 2em;
            }
            .back-btn {
                background: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                text-decoration: none;
                font-size: 14px;
            }
            .back-btn:hover {
                background: #7f8c8d;
                text-decoration: none;
                color: white;
            }
            
            .summary-cards {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }
            .summary-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                border-left: 5px solid #667eea;
            }
            .summary-card.income {
                border-left-color: #27ae60;
            }
            .summary-card.expense {
                border-left-color: #e74c3c;
            }
            .summary-card h3 {
                margin: 0 0 10px 0;
                color: #2c3e50;
                font-size: 1em;
            }
            .summary-card .amount {
                font-size: 1.8em;
                font-weight: bold;
                margin: 10px 0;
            }
            .summary-card.income .amount {
                color: #27ae60;
            }
            .summary-card.expense .amount {
                color: #e74c3c;
            }
            .summary-card.net .amount {
                color: {{ '#27ae60' if net_amount >= 0 else '#e74c3c' }};
            }
            
            .filters {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
            }
            .filters h3 {
                margin: 0 0 15px 0;
                color: #2c3e50;
            }
            .filter-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            }
            .filter-group input, .filter-group select {
                width: 100%;
                padding: 10px;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                font-size: 14px;
            }
            .filter-group input:focus, .filter-group select:focus {
                outline: none;
                border-color: #667eea;
            }
            .filter-btn {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
            }
            .filter-btn:hover {
                background: #5a6fd8;
            }
            
            .transactions-list {
                background: #f8f9fa;
                border-radius: 15px;
                overflow: hidden;
            }
            .transaction-item {
                background: white;
                margin: 10px;
                padding: 20px;
                border-radius: 10px;
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 20px;
                align-items: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .transaction-info {
                display: grid;
                gap: 5px;
            }
            .transaction-desc {
                font-size: 1.1em;
                font-weight: bold;
                color: #2c3e50;
            }
            .transaction-meta {
                font-size: 0.9em;
                color: #7f8c8d;
                display: flex;
                gap: 15px;
            }
            .transaction-amount {
                font-size: 1.3em;
                font-weight: bold;
                text-align: right;
            }
            .transaction-amount.income {
                color: #27ae60;
            }
            .transaction-amount.expense {
                color: #e74c3c;
            }
            .category-badge {
                background: #667eea;
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
            }
            .empty-state {
                text-align: center;
                color: #7f8c8d;
                padding: 60px 20px;
                font-size: 1.1em;
            }
            
            @media (max-width: 768px) {
                .summary-cards {
                    grid-template-columns: 1fr;
                }
                .filter-row {
                    grid-template-columns: 1fr;
                }
                .transaction-item {
                    grid-template-columns: 1fr;
                    gap: 10px;
                }
                .transaction-amount {
                    text-align: left;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 거래 내역</h1>
                <a href="/asset-manager/" class="back-btn">← 대시보드로</a>
            </div>
            
            <div class="summary-cards">
                <div class="summary-card income">
                    <h3>총 수입</h3>
                    <div class="amount">+₩{{ "{:,}".format(total_income) }}</div>
                </div>
                <div class="summary-card expense">
                    <h3>총 지출</h3>
                    <div class="amount">-₩{{ "{:,}".format(total_expense) }}</div>
                </div>
                <div class="summary-card net">
                    <h3>순 수지</h3>
                    <div class="amount">{{ '+' if net_amount >= 0 else '' }}₩{{ "{:,}".format(net_amount) }}</div>
                </div>
            </div>
            
            <div class="filters">
                <h3>🔍 필터</h3>
                <form method="GET">
                    <div class="filter-row">
                        <div class="filter-group">
                            <input type="date" name="start_date" placeholder="시작 날짜" value="{{ request.args.get('start_date', '') }}">
                        </div>
                        <div class="filter-group">
                            <input type="date" name="end_date" placeholder="종료 날짜" value="{{ request.args.get('end_date', '') }}">
                        </div>
                        <div class="filter-group">
                            <select name="category">
                                <option value="">전체 카테고리</option>
                                {% for cat in categories.income + categories.expense %}
                                <option value="{{ cat }}" {{ 'selected' if request.args.get('category') == cat else '' }}>{{ cat }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="filter-group">
                            <select name="type">
                                <option value="">수입/지출 전체</option>
                                <option value="income" {{ 'selected' if request.args.get('type') == 'income' else '' }}>수입만</option>
                                <option value="expense" {{ 'selected' if request.args.get('type') == 'expense' else '' }}>지출만</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="filter-btn">필터 적용</button>
                    <a href="/asset-manager/transactions" class="filter-btn" style="background: #95a5a6; text-decoration: none; margin-left: 10px;">초기화</a>
                </form>
            </div>
            
            <div class="transactions-list">
                {% if filtered_transactions %}
                    {% for transaction in filtered_transactions %}
                    <div class="transaction-item">
                        <div class="transaction-info">
                            <div class="transaction-desc">{{ transaction.description }}</div>
                            <div class="transaction-meta">
                                <span>📅 {{ transaction.date }}</span>
                                <span class="category-badge">{{ transaction.category }}</span>
                                <span>🕒 {{ transaction.created_at[:16] if transaction.created_at else '' }}</span>
                            </div>
                        </div>
                        <div class="transaction-amount {{ transaction.type }}">
                            {{ '+' if transaction.type == 'income' else '-' }}₩{{ "{:,}".format(transaction.amount) }}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        조건에 맞는 거래 내역이 없습니다.<br>
                        <small>다른 조건으로 검색해보세요.</small>
                    </div>
                {% endif %}
            </div>
            
            {% if filtered_transactions|length > 0 %}
            <div style="text-align: center; margin-top: 30px; color: #7f8c8d;">
                총 {{ filtered_transactions|length }}건의 거래 내역
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    
    from flask import render_template_string
    return render_template_string(transactions_html,
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
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #ecf0f1;
            }
            .header h1 {
                color: #2c3e50;
                margin: 0;
                font-size: 2em;
            }
            .back-btn {
                background: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                text-decoration: none;
                font-size: 14px;
            }
            .back-btn:hover {
                background: #7f8c8d;
                text-decoration: none;
                color: white;
            }
            
            .total-summary {
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 30px;
            }
            .total-amount {
                font-size: 3em;
                font-weight: bold;
                margin: 10px 0;
            }
            
            .asset-sections {
                display: grid;
                gap: 25px;
            }
            .asset-section {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                border-left: 5px solid #667eea;
            }
            .section-title {
                font-size: 1.3em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .asset-item {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .asset-item:last-child {
                margin-bottom: 0;
            }
            .asset-info h4 {
                margin: 0 0 5px 0;
                color: #2c3e50;
                font-size: 1.1em;
            }
            .asset-info p {
                margin: 0;
                color: #7f8c8d;
                font-size: 0.9em;
            }
            .asset-amount {
                font-size: 1.3em;
                font-weight: bold;
                color: #27ae60;
            }
            .empty-state {
                text-align: center;
                color: #7f8c8d;
                padding: 40px;
                font-style: italic;
            }
            .add-btn {
                background: #667eea;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                text-decoration: none;
                font-size: 14px;
                cursor: pointer;
                transition: background 0.3s ease;
            }
            .add-btn:hover {
                background: #5a6fd8;
                text-decoration: none;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 자산 현황</h1>
                <a href="/asset-manager/" class="back-btn">← 대시보드로</a>
            </div>
            
            <div class="total-summary">
                <h2>총 자산</h2>
                <div class="total-amount">₩{{ "{:,}".format(total_assets) }}</div>
                <p>모든 계좌 및 투자자산 합계</p>
            </div>
            
            <div class="asset-sections">
                <!-- 현금 -->
                <div class="asset-section">
                    <div class="section-title">
                        💵 현금
                        <button class="add-btn" onclick="updateCash()">수정</button>
                    </div>
                    <div class="asset-item">
                        <div class="asset-info">
                            <h4>{{ assets.cash.name if assets.cash else '현금' }}</h4>
                            <p>즉시 사용 가능한 현금</p>
                        </div>
                        <div class="asset-amount">₩{{ "{:,}".format(assets.cash.amount if assets.cash else 0) }}</div>
                    </div>
                </div>
                
                <!-- 은행 계좌 -->
                <div class="asset-section">
                    <div class="section-title">
                        🏦 은행 계좌
                        <button class="add-btn" onclick="addBankAccount()">계좌 추가</button>
                    </div>
                    {% if assets.bank_accounts %}
                        {% for account in assets.bank_accounts %}
                        <div class="asset-item">
                            <div class="asset-info">
                                <h4>{{ account.name }}</h4>
                                <p>{{ account.get('account_number', '계좌번호 미등록') }}</p>
                            </div>
                            <div class="asset-amount">₩{{ "{:,}".format(account.amount) }}</div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="empty-state">등록된 은행 계좌가 없습니다.</div>
                    {% endif %}
                </div>
                
                <!-- 투자 자산 -->
                <div class="asset-section">
                    <div class="section-title">
                        📈 투자 자산
                        <button class="add-btn" onclick="addInvestment()">투자 추가</button>
                    </div>
                    {% if assets.investments %}
                        {% for investment in assets.investments %}
                        <div class="asset-item">
                            <div class="asset-info">
                                <h4>{{ investment.name }}</h4>
                                <p>{{ investment.get('quantity', 0) }}주 @ ₩{{ "{:,}".format(investment.get('current_price', 0)) }}</p>
                            </div>
                            <div class="asset-amount">₩{{ "{:,}".format(investment.amount) }}</div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="empty-state">등록된 투자 자산이 없습니다.</div>
                    {% endif %}
                </div>
                
                <!-- 기타 자산 -->
                {% if assets.real_estate or assets.other %}
                <div class="asset-section">
                    <div class="section-title">
                        🏠 기타 자산
                        <button class="add-btn" onclick="addOtherAsset()">자산 추가</button>
                    </div>
                    {% for asset in assets.real_estate %}
                        <div class="asset-item">
                            <div class="asset-info">
                                <h4>{{ asset.name }}</h4>
                                <p>부동산</p>
                            </div>
                            <div class="asset-amount">₩{{ "{:,}".format(asset.amount) }}</div>
                        </div>
                    {% endfor %}
                    {% for asset in assets.other %}
                        <div class="asset-item">
                            <div class="asset-info">
                                <h4>{{ asset.name }}</h4>
                                <p>{{ asset.get('type', '기타') }}</p>
                            </div>
                            <div class="asset-amount">₩{{ "{:,}".format(asset.amount) }}</div>
                        </div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>
        
        <script>
            function updateCash() {
                const amount = prompt('현금 금액을 입력하세요 (원):', '{{ assets.cash.amount if assets.cash else 0 }}');
                if (amount !== null && !isNaN(amount)) {
                    // TODO: 현금 업데이트 API 호출
                    alert('현금 업데이트 기능은 준비 중입니다.');
                }
            }
            
            function addBankAccount() {
                alert('은행 계좌 추가 기능은 준비 중입니다.');
            }
            
            function addInvestment() {
                alert('투자 자산 추가 기능은 준비 중입니다.');
            }
            
            function addOtherAsset() {
                alert('기타 자산 추가 기능은 준비 중입니다.');
            }
        </script>
    </body>
    </html>
    """
    
    from flask import render_template_string
    return render_template_string(assets_html, 
                                assets=assets,
                                total_assets=total_assets)

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
