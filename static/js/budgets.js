// Budget Management JavaScript
document.addEventListener('DOMContentLoaded', () => {
    loadBudgets();
    loadCategories();
    
    // Set default dates
    const today = new Date();
    const startDate = new Date(today.getFullYear(), today.getMonth(), 1);
    const endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    document.getElementById('budgetStartDate').value = startDate.toISOString().split('T')[0];
    document.getElementById('budgetEndDate').value = endDate.toISOString().split('T')[0];
    
    // Form submit
    const form = document.getElementById('addBudgetForm');
    if (form) {
        form.addEventListener('submit', handleAddBudget);
    }
});

async function loadCategories() {
    try {
        const categories = await window.API.call('/categories');
        const select = document.getElementById('budgetCategory');
        if (select && categories) {
            const items = Array.isArray(categories) ? categories : (categories.items || []);
            items.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadBudgets() {
    const container = document.getElementById('budgetsContainer');
    if (!container) return;
    
    try {
        const budgets = await window.API.call('/budgets');
        if (budgets && budgets.length > 0) {
            displayBudgets(budgets);
        } else {
            container.innerHTML = `
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <div class="text-center py-5">
                                <i class="bi bi-inbox fs-1 text-muted d-block mb-3"></i>
                                <p class="text-muted mb-0">Chưa có ngân sách nào. Hãy tạo ngân sách đầu tiên của bạn!</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading budgets:', error);
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger" role="alert">
                    <i class="bi bi-exclamation-triangle"></i> Lỗi khi tải danh sách ngân sách.
                </div>
            </div>
        `;
    }
}

function displayBudgets(budgets) {
    const container = document.getElementById('budgetsContainer');
    
    const html = budgets.map(budget => {
        const periodText = {
            'monthly': 'Hàng tháng',
            'weekly': 'Hàng tuần',
            'yearly': 'Hàng năm'
        }[budget.period] || budget.period;
        
        return `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h6 class="card-title mb-0">
                                <span class="badge bg-primary">${budget.category_name}</span>
                            </h6>
                            <span class="badge bg-${budget.is_active ? 'success' : 'secondary'}">
                                ${budget.is_active ? 'Đang hoạt động' : 'Tạm dừng'}
                            </span>
                        </div>
                        <p class="mb-2">
                            <strong>Số tiền:</strong> 
                            <span class="text-primary fs-5">${formatCurrency(budget.amount)}</span>
                        </p>
                        <p class="mb-2">
                            <strong>Chu kỳ:</strong> ${periodText}
                        </p>
                        <p class="mb-2 small text-muted">
                            <i class="bi bi-calendar"></i> 
                            ${formatDate(budget.start_date)} - ${formatDate(budget.end_date)}
                        </p>
                        <div class="mt-3">
                            <button class="btn btn-sm btn-outline-primary" onclick="viewBudgetStatus(${budget.id})">
                                <i class="bi bi-graph-up"></i> Xem trạng thái
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteBudget(${budget.id})">
                                <i class="bi bi-trash"></i> Xóa
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

async function handleAddBudget(e) {
    e.preventDefault();
    
    const categoryId = document.getElementById('budgetCategory').value;
    const amount = document.getElementById('budgetAmount').value;
    const period = document.getElementById('budgetPeriod').value;
    const startDate = document.getElementById('budgetStartDate').value;
    const endDate = document.getElementById('budgetEndDate').value;
    
    if (!categoryId || !amount || !startDate || !endDate) {
        showAlert('Vui lòng điền đầy đủ thông tin', 'warning');
        return;
    }
    
    try {
        const result = await window.API.call('/budgets', {
            method: 'POST',
            body: JSON.stringify({
                category_id: parseInt(categoryId),
                amount: amount,
                period: period,
                start_date: startDate,
                end_date: endDate
            })
        });
        
        if (result) {
            showAlert('Tạo ngân sách thành công!', 'success');
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addBudgetModal'));
            if (modal) modal.hide();
            // Reset form
            document.getElementById('addBudgetForm').reset();
            // Reload budgets
            loadBudgets();
        }
    } catch (error) {
        console.error('Error creating budget:', error);
        showAlert('Lỗi khi tạo ngân sách. Vui lòng thử lại.', 'danger');
    }
}

async function viewBudgetStatus(budgetId) {
    try {
        const status = await window.API.call(`/budgets/${budgetId}/status`);
        if (status) {
            const percentage = status.percentage || 0;
            const statusClass = percentage >= 100 ? 'danger' : (percentage >= 80 ? 'warning' : 'success');
            
            const html = `
                <div class="alert alert-${statusClass}" role="alert">
                    <h6><i class="bi bi-graph-up"></i> Trạng thái Ngân sách</h6>
                    <p class="mb-2"><strong>Danh mục:</strong> ${status.category}</p>
                    <p class="mb-2"><strong>Ngân sách:</strong> ${formatCurrency(status.amount)}</p>
                    <p class="mb-2"><strong>Đã chi:</strong> ${formatCurrency(status.spent)}</p>
                    <p class="mb-2"><strong>Còn lại:</strong> ${formatCurrency(status.remaining)}</p>
                    <div class="progress mt-2" style="height: 25px;">
                        <div class="progress-bar bg-${statusClass}" role="progressbar" style="width: ${Math.min(percentage, 100)}%">
                            ${percentage.toFixed(1)}%
                        </div>
                    </div>
                </div>
            `;
            
            showModal('Trạng thái Ngân sách', html);
        }
    } catch (error) {
        console.error('Error loading budget status:', error);
        showAlert('Lỗi khi tải trạng thái ngân sách', 'danger');
    }
}

async function deleteBudget(budgetId) {
    if (!confirm('Bạn có chắc chắn muốn xóa ngân sách này?')) {
        return;
    }
    
    try {
        const result = await window.API.call(`/budgets/${budgetId}`, {
            method: 'DELETE'
        });
        
        if (result && result.success) {
            showAlert('Xóa ngân sách thành công!', 'success');
            loadBudgets();
        }
    } catch (error) {
        console.error('Error deleting budget:', error);
        showAlert('Lỗi khi xóa ngân sách', 'danger');
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function showModal(title, content) {
    // Create and show modal
    const modalHtml = `
        <div class="modal fade" id="infoModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existing = document.getElementById('infoModal');
    if (existing) existing.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('infoModal'));
    modal.show();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(parseFloat(amount || 0));
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

