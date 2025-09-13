# Asset Manager Module

개인 자산 관리 및 가계부 기능을 제공하는 모듈입니다.

## 📋 주요 기능

### 1. 거래 내역 관리
- 수입/지출 기록
- 카테고리별 분류
- 날짜별 조회 및 필터링

### 2. 자산 관리
- 현금 관리
- 은행 계좌 관리
- 투자 자산 추적
- 부동산 등 기타 자산

### 3. 분석 및 통계
- 월별 수입/지출 분석
- 카테고리별 지출 패턴
- 자산 증감 추이

### 4. 카테고리 관리
- 수입/지출 카테고리 설정
- 사용자 정의 카테고리 추가

## 🚀 API 엔드포인트

### 거래 내역 API
- `GET /asset-manager/transactions` - 거래 내역 조회
- `POST /asset-manager/transactions` - 거래 내역 추가

### 자산 관리 API
- `GET /asset-manager/assets` - 자산 현황 조회

### 분석 API
- `GET /asset-manager/analysis` - 지출 분석 데이터

### 카테고리 API
- `GET /asset-manager/categories` - 카테고리 조회

### 기타
- `GET /asset-manager/` - 대시보드
- `GET /asset-manager/health` - 헬스 체크

## 📊 데이터 구조

### 거래 내역 (transactions.json)
```json
{
  "id": "20250903_143022",
  "date": "2025-09-03",
  "amount": 50000,
  "category": "급여",
  "type": "income",
  "description": "월급",
  "created_at": "2025-09-03T14:30:22"
}
```

### 자산 현황 (assets.json)
```json
{
  "cash": {
    "name": "현금",
    "amount": 100000,
    "currency": "KRW"
  },
  "bank_accounts": [
    {
      "name": "신한은행 주계좌",
      "amount": 1000000,
      "account_number": "****1234"
    }
  ],
  "investments": [
    {
      "name": "삼성전자 주식",
      "amount": 500000,
      "quantity": 10,
      "current_price": 50000
    }
  ]
}
```

### 카테고리 (categories.json)
```json
{
  "income": ["급여", "부업", "투자수익", "기타수입"],
  "expense": ["식비", "교통비", "주거비", "의료비", "쇼핑", "여가", "교육", "기타지출"]
}
```

## 🔧 사용 방법

### 1. 거래 내역 추가
```bash
curl -X POST http://localhost:5000/asset-manager/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "category": "식비",
    "type": "expense",
    "description": "점심식사",
    "date": "2025-09-03"
  }'
```

### 2. 거래 내역 조회
```bash
# 전체 조회
curl http://localhost:5000/asset-manager/transactions

# 날짜별 조회
curl "http://localhost:5000/asset-manager/transactions?start_date=2025-09-01&end_date=2025-09-30"

# 카테고리별 조회
curl "http://localhost:5000/asset-manager/transactions?category=식비"
```

### 3. 자산 현황 조회
```bash
curl http://localhost:5000/asset-manager/assets
```

### 4. 지출 분석
```bash
curl http://localhost:5000/asset-manager/analysis
```

## 📁 파일 구조

```
asset-manager/
├── sub_app.py          # 메인 Flask 앱
├── README.md           # 이 파일
├── data/               # 데이터 저장 디렉토리
│   ├── transactions.json   # 거래 내역
│   ├── assets.json         # 자산 현황
│   └── categories.json     # 카테고리 설정
└── LICENSE             # 라이선스 파일
```

## 🔒 보안

- 모든 API는 메인 서버의 Google OAuth 인증이 필요합니다
- 데이터는 로컬 JSON 파일에 저장됩니다
- 민감한 정보 (계좌번호 등)는 마스킹 처리됩니다

## 🚧 향후 개발 계획

- [ ] 데이터베이스 연동 (SQLite/PostgreSQL)
- [ ] 파일 업로드를 통한 일괄 거래 내역 등록
- [ ] 예산 설정 및 알림 기능
- [ ] 차트 및 그래프 시각화
- [ ] CSV/Excel 내보내기 기능
- [ ] 자동 카테고리 분류 (AI 기반)
- [ ] 은행 API 연동을 통한 자동 거래 내역 동기화

## 📞 지원

문의사항이 있으시면 메인 서버 관리자에게 연락해주세요.
