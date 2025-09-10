/**
 * Asset Manager Dashboard JavaScript
 * SQLite 기반 API와 연동하는 프론트엔드 기능들
 */

// 전역 변수
let categories = [];
let currentTransactionType = '';

/**
 * 페이지 초기화
 */
function initializeDashboard() {
    loadCategories();
    setTodayDate();
    bindFormEvents();
}

/**
 * 카테고리 목록 로드
 */
async function loadCategories() {
    try {
        const response = await fetch('/asset-manager/api/categories');
        const data = await response.json();
        
        if (data.status === 'success') {
            categories = data.categories;
            console.log('카테고리 로드 완료:', categories.length, '개');
        } else {
            console.error('카테고리 로드 실패:', data.message);
            showNotification('카테고리를 불러오는데 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('카테고리 로드 중 오류:', error);
        showNotification('서버 연결에 실패했습니다.', 'error');
    }
}

/**
 * 거래 내역 추가 폼 표시
 */
function showAddTransaction(type) {
    currentTransactionType = type;
    
    // 폼 제목 설정
    const formTitle = document.getElementById('form-title');
    formTitle.textContent = type === 'income' ? '💰 수입 등록' : '💸 지출 등록';
    
    // 타입 설정
    document.getElementById('type').value = type;
    
    // 카테고리 옵션 업데이트
    updateCategoryOptions(type);
    
    // 폼 표시
    document.getElementById('transaction-form').style.display = 'flex';
    
    // 첫 번째 입력 필드에 포커스
    document.getElementById('amount').focus();
}

/**
 * 폼 숨기기
 */
function hideForm() {
    document.getElementById('transaction-form').style.display = 'none';
    resetForm();
}

/**
 * 폼 리셋
 */
function resetForm() {
    document.getElementById('add-transaction-form').reset();
    setTodayDate();
}

/**
 * 오늘 날짜 설정
 */
function setTodayDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
}

/**
 * 카테고리 옵션 업데이트
 */
function updateCategoryOptions(type) {
    const categorySelect = document.getElementById('category_id');
    categorySelect.innerHTML = '<option value="">카테고리를 선택하세요</option>';
    
    const filteredCategories = categories.filter(cat => cat.type === type);
    
    filteredCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.appendChild(option);
    });
}

/**
 * 폼 이벤트 바인딩
 */
function bindFormEvents() {
    const form = document.getElementById('add-transaction-form');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitTransaction();
    });
    
    // ESC 키로 폼 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideForm();
        }
    });
    
    // 배경 클릭으로 폼 닫기
    document.getElementById('transaction-form').addEventListener('click', function(e) {
        if (e.target === this) {
            hideForm();
        }
    });
}

/**
 * 거래 내역 제출
 */
async function submitTransaction() {
    const formData = new FormData(document.getElementById('add-transaction-form'));
    const data = {
        type: formData.get('type'),
        amount: parseFloat(formData.get('amount')),
        category_id: parseInt(formData.get('category_id')),
        description: formData.get('description') || '',
        date: formData.get('date')
    };
    
    // 유효성 검사
    if (!validateTransactionData(data)) {
        return;
    }
    
    try {
        // 제출 버튼 비활성화
        const submitBtn = document.querySelector('#add-transaction-form button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = '등록 중...';
        
        const response = await fetch('/asset-manager/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showNotification(
                `${data.type === 'income' ? '수입' : '지출'} 내역이 성공적으로 등록되었습니다!`,
                'success'
            );
            hideForm();
            // 페이지 새로고침으로 업데이트된 데이터 표시
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(`등록 실패: ${result.message}`, 'error');
        }
        
    } catch (error) {
        console.error('거래 내역 등록 중 오류:', error);
        showNotification('서버 연결에 실패했습니다.', 'error');
    } finally {
        // 제출 버튼 복원
        const submitBtn = document.querySelector('#add-transaction-form button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

/**
 * 거래 데이터 유효성 검사
 */
function validateTransactionData(data) {
    if (!data.type || !['income', 'expense'].includes(data.type)) {
        showNotification('올바른 거래 타입을 선택해주세요.', 'error');
        return false;
    }
    
    if (!data.amount || data.amount <= 0) {
        showNotification('금액은 0보다 큰 값을 입력해주세요.', 'error');
        document.getElementById('amount').focus();
        return false;
    }
    
    if (!data.category_id) {
        showNotification('카테고리를 선택해주세요.', 'error');
        document.getElementById('category_id').focus();
        return false;
    }
    
    if (!data.date) {
        showNotification('날짜를 선택해주세요.', 'error');
        document.getElementById('date').focus();
        return false;
    }
    
    return true;
}

/**
 * 알림 메시지 표시
 */
function showNotification(message, type = 'info') {
    // 기존 알림 제거
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // 새 알림 생성
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // 페이지 상단에 추가
    document.body.insertBefore(notification, document.body.firstChild);
    
    // 자동 제거 (5초 후)
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// CSS 스타일을 동적으로 추가
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .notification-success {
        background-color: #27ae60;
    }
    
    .notification-error {
        background-color: #e74c3c;
    }
    
    .notification-info {
        background-color: #3498db;
    }
    
    .notification button {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        margin-left: 10px;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .notification button:hover {
        opacity: 0.8;
    }
    
    .form-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .form-overlay form {
        background: white;
        padding: 30px;
        border-radius: 10px;
        width: 90%;
        max-width: 500px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
`;
document.head.appendChild(style);
