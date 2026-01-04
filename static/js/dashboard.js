// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    
    // Auto-refresh every 5 minutes
    setInterval(loadDashboardData, 5 * 60 * 1000);
});

// Expose to window for other scripts to trigger updates
window.loadDashboardData = loadDashboardData;

async function loadDashboardData() {
    try {
        // Load summary
        const summary = await window.API.call(`/dashboard/summary?v=${Date.now()}`);
        if (summary) {
            displaySummary(summary);
        }
        
        // Load category breakdown
        const breakdown = await window.API.call(`/dashboard/category-breakdown?v=${Date.now()}`);
        if (breakdown) {
            displayCategoryBreakdown(breakdown);
        }
        
        // Load monthly comparison
        const monthly = await window.API.call(`/dashboard/monthly-comparison?months=6&v=${Date.now()}`);
        if (monthly) {
            displayMonthlyComparison(monthly);
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Assuming this function is meant to be a separate utility for deleting transactions
// and not part of loadDashboardData or displayCategoryBreakdown
async function deleteTransaction(id) {
    try {
        const response = await fetch(`/api/v1/transactions/${id}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            // Show toast/notification instead of alert
            showToast('Đã xóa giao dịch thành công!', 'success');
            // Assuming loadTransactions() is defined elsewhere to refresh transaction list
            // loadTransactions(); 
            // Update dashboard if function exists
            if (typeof window.loadDashboardData === 'function') {
                window.loadDashboardData();
            }
        } else {
            showToast('Lỗi khi xóa giao dịch', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Lỗi kết nối', 'error');
    }
}

function showToast(message, type = 'info') {
    // Simple toast implementation or usage of existing one
    // Check if we have a toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    const bgClass = type === 'success' ? 'bg-success' : (type === 'error' ? 'bg-danger' : 'bg-primary');
    
    const toastHtml = `
        <div class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    const toastWrapper = document.createElement('div');
    toastWrapper.innerHTML = toastHtml;
    const toastEl = toastWrapper.firstElementChild;
    toastContainer.appendChild(toastEl);
    
    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();
    
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

function displaySummary(data) {
    // Update summary cards
    const incomeEl = document.getElementById('income');
    const expenseEl = document.getElementById('expense');
    const balanceEl = document.getElementById('balance');
    
    if (incomeEl) incomeEl.textContent = '+' + formatCurrency(data.total_income);
    if (expenseEl) expenseEl.textContent = '-' + formatCurrency(data.total_expense);
    // Use current_balance (Total Wallet Balance) instead of period balance (Net Income)
    if (balanceEl) balanceEl.textContent = formatCurrency(data.current_balance);
}

function displayCategoryBreakdown(data) {
    const categoryBreakdown = document.getElementById('categoryBreakdown');
    if (!categoryBreakdown) return;
    
    if (!data || data.length === 0) {
        categoryBreakdown.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-pie-chart fs-1 text-muted d-block mb-3"></i>
                <p class="text-muted mb-0">Chưa có chi tiêu nào. Hãy tạo giao dịch chi tiêu đầu tiên để xem phân bổ!</p>
            </div>
        `;
        return;
    }
    
    // Calculate total for percentage
    const total = data.reduce((sum, cat) => sum + parseFloat(cat.amount || 0), 0);
    
    // Check if there's any actual data
    if (total === 0) {
        categoryBreakdown.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-pie-chart fs-1 text-muted d-block mb-3"></i>
                <p class="text-muted mb-0">Chưa có chi tiêu nào. Hãy tạo giao dịch chi tiêu đầu tiên để xem phân bổ!</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    data.forEach(cat => {
        const amount = parseFloat(cat.amount || 0);
        if (amount === 0) return; // Skip categories with zero amount
        
        const percentage = total > 0 ? ((amount / total) * 100).toFixed(1) : 0;
        html += `
            <div class="list-group-item border-0 px-0">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span><strong>${cat.category || 'Không có danh mục'}</strong></span>
                    <span class="badge bg-primary">${formatCurrency(amount)}</span>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar" role="progressbar" style="width: ${percentage}%" aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <small class="text-muted">${percentage}%</small>
            </div>
        `;
    });
    html += '</div>';
    
    // If no categories were added (all were skipped), show empty message
    if (html === '<div class="list-group list-group-flush">') {
        categoryBreakdown.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-pie-chart fs-1 text-muted d-block mb-3"></i>
                <p class="text-muted mb-0">Chưa có chi tiêu nào. Hãy tạo giao dịch chi tiêu đầu tiên để xem phân bổ!</p>
            </div>
        `;
    } else {
        categoryBreakdown.innerHTML = html;
    }
}

function displayMonthlyComparison(data) {
    const monthlyComparison = document.getElementById('monthlyComparison');
    if (!monthlyComparison) return;
    
    if (!data || data.length === 0) {
        monthlyComparison.innerHTML = '<p class="text-muted text-center py-4">Chưa có dữ liệu</p>';
        return;
    }
    
    // Check if there's any actual data (not all zeros)
    const hasData = data.some(month => month.income > 0 || month.expense > 0);
    
    if (!hasData) {
        monthlyComparison.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-inbox fs-1 text-muted d-block mb-3"></i>
                <p class="text-muted mb-0">Chưa có giao dịch nào. Hãy tạo giao dịch đầu tiên để xem thống kê!</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    data.forEach(month => {
        // Only show months with actual data
        if (month.income === 0 && month.expense === 0) {
            return; // Skip months with no data
        }
        
        const balanceClass = month.balance >= 0 ? 'text-success' : 'text-danger';
        html += `
            <div class="list-group-item border-0 px-0">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <strong>${month.month}</strong>
                    <span class="badge bg-${month.balance >= 0 ? 'success' : 'danger'}">${formatCurrency(month.balance)}</span>
                </div>
                <div class="row g-2 small">
                    <div class="col-4">
                        <span class="text-muted">Thu:</span>
                        <span class="text-success">${formatCurrency(month.income)}</span>
                    </div>
                    <div class="col-4">
                        <span class="text-muted">Chi:</span>
                        <span class="text-danger">${formatCurrency(month.expense)}</span>
                    </div>
                    <div class="col-4">
                        <span class="text-muted">Còn lại:</span>
                        <span class="${balanceClass}">${formatCurrency(month.balance)}</span>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // If no months were added (all were skipped), show empty message
    if (html === '<div class="list-group list-group-flush">') {
        monthlyComparison.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-inbox fs-1 text-muted d-block mb-3"></i>
                <p class="text-muted mb-0">Chưa có giao dịch nào. Hãy tạo giao dịch đầu tiên để xem thống kê!</p>
            </div>
        `;
    } else {
        monthlyComparison.innerHTML = html;
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
