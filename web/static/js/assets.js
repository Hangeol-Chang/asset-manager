// 자산 관리 JavaScript 기능

function updateCash() {
    const currentAmount = document.querySelector('.asset-category:first-child .asset-amount').textContent.replace(/[^\d]/g, '');
    const amount = prompt('현금 금액을 입력하세요 (원):', currentAmount);
    
    if (amount !== null && !isNaN(amount) && amount !== '') {
        // TODO: 현금 업데이트 API 호출
        alert('현금 업데이트 기능은 준비 중입니다.');
    }
}

function addBankAccount() {
    const name = prompt('은행 계좌명을 입력하세요:', '');
    if (name) {
        const accountNumber = prompt('계좌번호를 입력하세요 (선택사항):', '');
        const amount = prompt('잔액을 입력하세요 (원):', '0');
        
        if (amount !== null && !isNaN(amount)) {
            // TODO: 은행 계좌 추가 API 호출
            alert('은행 계좌 추가 기능은 준비 중입니다.');
        }
    }
}

function addInvestment() {
    const name = prompt('투자 상품명을 입력하세요:', '');
    if (name) {
        const quantity = prompt('보유 수량을 입력하세요:', '0');
        const currentPrice = prompt('현재 가격을 입력하세요 (원):', '0');
        
        if (quantity !== null && currentPrice !== null && !isNaN(quantity) && !isNaN(currentPrice)) {
            // TODO: 투자 자산 추가 API 호출
            alert('투자 자산 추가 기능은 준비 중입니다.');
        }
    }
}

function addOtherAsset() {
    const name = prompt('자산명을 입력하세요:', '');
    if (name) {
        const type = prompt('자산 유형을 입력하세요 (예: 부동산, 자동차 등):', '기타');
        const amount = prompt('가치를 입력하세요 (원):', '0');
        
        if (amount !== null && !isNaN(amount)) {
            // TODO: 기타 자산 추가 API 호출
            alert('기타 자산 추가 기능은 준비 중입니다.');
        }
    }
}
