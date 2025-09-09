// 대시보드 JavaScript 기능

// 오늘 날짜를 기본값으로 설정
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
});

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
    const categoryList = type === 'income' ? window.categories.income : window.categories.expense;
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
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-transaction-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
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
    }
});
