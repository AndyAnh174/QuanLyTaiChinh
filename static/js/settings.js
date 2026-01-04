// Settings JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Change access code form
    const form = document.getElementById('changeAccessCodeForm');
    if (form) {
        form.addEventListener('submit', handleChangeAccessCode);
    }
});

async function handleChangeAccessCode(e) {
    e.preventDefault();
    
    const oldCode = document.getElementById('oldAccessCode').value;
    const newCode = document.getElementById('newAccessCode').value;
    const confirmCode = document.getElementById('confirmAccessCode').value;
    
    if (newCode !== confirmCode) {
        showAlert('Mã truy cập mới và xác nhận không khớp', 'danger');
        return;
    }
    
    if (newCode.length < 4) {
        showAlert('Mã truy cập mới phải có ít nhất 4 ký tự', 'warning');
        return;
    }
    
    try {
        const result = await window.API.call('/auth/change', {
            method: 'POST',
            body: JSON.stringify({
                old_code: oldCode,
                new_code: newCode
            })
        });
        
        if (result && result.success) {
            showAlert('Đổi mã truy cập thành công! Vui lòng đăng nhập lại.', 'success');
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('changeAccessCodeModal'));
            if (modal) modal.hide();
            // Reset form
            document.getElementById('changeAccessCodeForm').reset();
            // Redirect to access code page after 2 seconds
            setTimeout(() => {
                window.location.href = '/auth/access-code';
            }, 2000);
        } else {
            showAlert(result?.error || 'Lỗi khi đổi mã truy cập', 'danger');
        }
    } catch (error) {
        console.error('Error changing access code:', error);
        showAlert('Lỗi khi đổi mã truy cập. Vui lòng thử lại.', 'danger');
    }
}

async function exportData() {
    try {
        showAlert('Đang xuất dữ liệu...', 'info');
        
        // Get all transactions
        const transactions = await window.API.call('/transactions?limit=10000');
        const items = Array.isArray(transactions) ? transactions : (transactions?.items || []);
        
        if (items.length === 0) {
            showAlert('Không có dữ liệu để xuất', 'warning');
            return;
        }
        
        // Convert to CSV
        const headers = ['ID', 'Ngày', 'Mô tả', 'Danh mục', 'Ví', 'Số tiền', 'Loại', 'Người liên hệ'];
        const rows = items.map(tx => [
            tx.id,
            tx.date,
            tx.description || '',
            tx.category_name || '',
            tx.wallet_name || '',
            tx.amount,
            tx.transaction_type,
            tx.contact_person || ''
        ]);
        
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        ].join('\n');
        
        // Download
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `transactions_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showAlert('Xuất dữ liệu thành công!', 'success');
    } catch (error) {
        console.error('Error exporting data:', error);
        showAlert('Lỗi khi xuất dữ liệu', 'danger');
    }
}

// Show Delete Modal
function confirmDeleteData() {
    // Reset modal state
    const input = document.getElementById('deleteConfirmationInput');
    const btn = document.getElementById('confirmDeleteBtn');
    
    if (input) {
        input.value = '';
        input.classList.remove('is-valid', 'is-invalid');
    }
    if (btn) btn.disabled = true;

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('deleteDataModal'));
    modal.show();
    
    // Add real-time validation listener if not already added (simple check to avoid dupes or just re-add)
    if (input) {
        input.onkeyup = function() {
            if (this.value === 'XÓA TẤT CẢ') {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
                btn.disabled = false;
            } else {
                this.classList.remove('is-valid');
                // Optional: Show invalid if length is close but wrong? Nah, keep simple.
                btn.disabled = true;
            }
        };
    }
}

async function executeDeleteData() {
    // Hide modal
    const modalEl = document.getElementById('deleteDataModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
    
    try {
        showAlert('Đang xóa dữ liệu...', 'warning');
        
        // Get all transactions and delete them (Backend integration)
        // Note: Ideally backend should have a "reset" endpoint, but we loop delete here as per existing logic
        const transactions = await window.API.call('/transactions?limit=10000');
        const items = Array.isArray(transactions) ? transactions : (transactions?.items || []);
        
        // Delete each transaction
        for (const tx of items) {
            try {
                await window.API.call(`/transactions/${tx.id}`, {
                    method: 'DELETE'
                });
            } catch (e) {
                console.error(`Error deleting transaction ${tx.id}:`, e);
            }
        }
        
        // Get all budgets and delete them
        const budgets = await window.API.call('/budgets');
        if (budgets && Array.isArray(budgets)) {
            for (const budget of budgets) {
                try {
                    await window.API.call(`/budgets/${budget.id}`, {
                        method: 'DELETE'
                    });
                } catch (e) {
                    console.error(`Error deleting budget ${budget.id}:`, e);
                }
            }
        }
        
        showAlert('Đã xóa tất cả dữ liệu thành công!', 'success');
        
        // Reload page after 2 seconds
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    } catch (error) {
        console.error('Error deleting data:', error);
        showAlert('Lỗi khi xóa dữ liệu', 'danger');
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
    }, 5000);
}

