/* transactions.js - Full functionality */

let editingTransactionId = null;
let wallets = [];
let categories = [];

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Tabs
    const listTab = document.getElementById('list-tab');
    if (listTab) {
        listTab.addEventListener('shown.bs.tab', loadTransactions);
    }
    
    // Initialize Modal
    const modalElement = document.getElementById('addTransactionModal');
    if (modalElement) {
        modalElement.addEventListener('show.bs.modal', loadReferenceData);
        modalElement.addEventListener('hidden.bs.modal', resetModal);
    }
    
    // Set default date
    const dateInput = document.getElementById('transDate');
    if (dateInput) {
        dateInput.valueAsDate = new Date();
    }
    
    // Quick Add Form
    const quickAddForm = document.getElementById('quickAddForm');
    if (quickAddForm) {
        quickAddForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processQuickAdd();
        });
    }

    // Upload Form
    const uploadForm = document.getElementById('uploadReceiptForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processUpload();
        });
        
        // File Input Preview
        const fileInput = document.getElementById('receiptFile');
        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.getElementById('previewImage');
                        const previewDiv = document.getElementById('uploadPreview');
                        if(preview) preview.src = e.target.result;
                        if(previewDiv) previewDiv.style.display = 'block';
                    }
                    reader.readAsDataURL(file);
                }
            });
        }
    }
    
    // Initial Load if List is active
    if (listTab && listTab.classList.contains('active')) {
        loadTransactions();
        // Populate filter wallet select
        loadReferenceDataForFilter();
    }
});

async function loadReferenceDataForFilter() {
    try {
        const response = await fetch('/api/v1/wallets');
        if (!response.ok) return;
        const wallets = await response.json();
        const select = document.getElementById('filterWallet');
        if (!select) return;
        
        // Keep first option
        const firstOption = select.options[0];
        select.innerHTML = '';
        select.appendChild(firstOption);
        
        wallets.forEach(w => {
            select.innerHTML += `<option value="${w.id}">${w.name}</option>`;
        });
    } catch(e) { console.error(e); }
}

/* --- API Functions --- */

async function loadTransactions() {
    const container = document.getElementById('transactionsContainer');
    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-3 text-muted">Đang tải dữ liệu...</p>
        </div>
    `;
    
    try {
        // Build URL with filters
        const startDate = document.getElementById('filterStartDate')?.value;
        const endDate = document.getElementById('filterEndDate')?.value;
        const walletId = document.getElementById('filterWallet')?.value;
        const type = document.getElementById('filterType')?.value;
        
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (walletId) params.append('wallet_id', walletId);
        if (type) params.append('transaction_type', type);
        
        const response = await fetch(`/api/v1/transactions?${params.toString()}`);
        const transactions = await response.json();
        renderTransactions(transactions);
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `<div class="alert alert-danger">Lỗi tải dữ liệu.</div>`;
    }
}

function renderTransactions(transactions) {
    const container = document.getElementById('transactionsContainer');
    if (!transactions || transactions.length === 0) {
        container.innerHTML = `<div class="alert alert-info text-center">Chưa có giao dịch nào.</div>`;
        return;
    }
    
    let html = `
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-light">
                    <tr>
                        <th>Ngày</th>
                        <th>Mô tả</th>
                        <th>Danh mục</th>
                        <th>Ví</th>
                        <th class="text-end">Số tiền</th>
                        <th class="text-center" style="width: 120px;">Hành động</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    transactions.forEach(tx => {
        const amountClass = tx.transaction_type === 'income' ? 'text-success' : 'text-danger';
        const sign = tx.transaction_type === 'income' ? '+' : '-';
        const displayAmount = `${sign}${formatCurrency(tx.amount)}`;
        const dateStr = new Date(tx.date).toLocaleDateString('vi-VN');
        
        html += `
            <tr>
                <td>${dateStr}</td>
                <td class="fw-bold">${tx.description || 'Không mô tả'}</td>
                <td><span class="badge bg-secondary">${tx.category_name || 'Khác'}</span></td>
                <td>${tx.wallet_name}</td>
                <td class="text-end ${amountClass} fw-bold">${displayAmount}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editTransaction(${tx.id})" title="Sửa">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTransaction(${tx.id})" title="Xóa">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += `</tbody></table></div>`;
    container.innerHTML = html;
    html += `</tbody></table></div>`;
    container.innerHTML = html;
}

function resetFilters() {
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    document.getElementById('filterWallet').value = '';
    document.getElementById('filterType').value = '';
    loadTransactions();
}

async function loadReferenceData() {
    try {
        const [wRes, cRes] = await Promise.all([
            fetch('/api/v1/wallets'),
            fetch('/api/v1/categories')
        ]);
        
        wallets = await wRes.json();
        categories = await cRes.json();
        
        // Populate Wallet Select
        const wSelect = document.getElementById('transWallet');
        const currentWalletId = wSelect.value;
        wSelect.innerHTML = '<option value="">-- Chọn ví --</option>';
        wallets.forEach(w => {
            wSelect.innerHTML += `<option value="${w.id}">${w.name} (${formatCurrency(w.balance)})</option>`;
        });
        if(currentWalletId) wSelect.value = currentWalletId;
        
        // Populate Category Select
        const cSelect = document.getElementById('transCategory');
        const currentCatId = cSelect.value;
        cSelect.innerHTML = '<option value="">-- Chọn danh mục --</option>';
        categories.forEach(c => {
            cSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
        });
        if(currentCatId) cSelect.value = currentCatId;
        
    } catch (e) {
        console.error("Error loading reference data", e);
    }
}

async function processQuickAdd() {
    const text = document.getElementById('quickAddText').value;
    if (!text) return;
    
    const btn = document.querySelector('#quickAddForm button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Đang xử lý...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/v1/transactions/parse/quick-add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: text})
        });
        const data = await response.json();
        
        // Render preview results
        const resultDiv = document.getElementById('quickAddResults');
        resultDiv.style.display = 'block';
        if (data.transactions && data.transactions.length > 0) {
            let html = `<h6>Kết quả phân tích:</h6><div class="list-group">`;
            data.transactions.forEach((tx) => {
                // Determine display type based on NLP result
                const isIncome = (tx.transaction_type === 'income');
                const typeLabel = isIncome 
                    ? '<span class="badge bg-success">Thu nhập</span>' 
                    : '<span class="badge bg-danger">Chi tiêu</span>';
                
                // Escape JSON for onclick
                const txString = JSON.stringify(tx).replace(/"/g, '&quot;');
                
                html += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${tx.description}</h5>
                            <small>${typeLabel}</small>
                        </div>
                        <p class="mb-1">Số tiền: <strong>${formatCurrency(tx.amount)}</strong> | Ví: ${tx.wallet_name} | Danh mục: ${tx.category_name}</p>
                        <button class="btn btn-sm btn-primary mt-2" onclick="saveQuickTransaction(${txString}, this)">
                            <i class="bi bi-check"></i> Xác nhận tạo
                        </button>
                    </div>
                `;
            });
            html += `</div>`;
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = `<div class="alert alert-warning">Không tìm thấy giao dịch nào.</div>`;
        }
        
    } catch (e) {
        alert('Lỗi khi xử lý quick add: ' + e);
        console.error(e);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function saveQuickTransaction(txData, btnElement) {
    const payload = {
        amount: txData.amount.toString(),
        description: txData.description,
        wallet_id: txData.wallet_id,
        category_id: txData.category_id,
        transaction_type: txData.transaction_type || 'expense', // Important: use detected type
        date: txData.date,
        contact_person: null
    };
    
    try {
        const response = await fetch('/api/v1/transactions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            // Success State
            // Use passed element or fallback (though fallback is fragile)
            const btn = btnElement || document.querySelector(`button[onclick='saveQuickTransaction(${JSON.stringify(txData).replace(/"/g, '&quot;')})']`);
            if (btn) {
                const cardBody = btn.closest('.list-group-item, .card-body');
                if (cardBody) {
                    cardBody.innerHTML = `
                        <div class="alert alert-success border-2 border-dark mb-0">
                            <i class="bi bi-check-circle-fill"></i> Đã tạo giao dịch thành công!
                        </div>
                    `;
                    // Auto fade out logic could go here, or just leave as confirmation
                    setTimeout(() => {
                        const item = cardBody.closest('.list-group-item');
                        if (item) item.remove();
                        else if (cardBody.closest('#uploadResults')) {
                            document.getElementById('uploadResults').style.display = 'none';
                        }
                    }, 2000);
                }
            }
            
            // Refresh dashboard data
            if (typeof window.loadDashboardData === 'function') {
                window.loadDashboardData();
            }
             // Refresh list if active
            const listTab = document.getElementById('list-tab');
            if (listTab && listTab.classList.contains('active')) {
                loadTransactions();
            }
        } else {
            const err = await response.json();
            const btn = btnElement || document.querySelector(`button[onclick='saveQuickTransaction(${JSON.stringify(txData).replace(/"/g, '&quot;')})']`);
            if (btn) {
                 const errorDiv = document.createElement('div');
                 errorDiv.className = 'alert alert-danger mt-2';
                 errorDiv.innerText = 'Lỗi: ' + (err.message || 'Server Error');
                 btn.parentElement.appendChild(errorDiv);
                 setTimeout(() => errorDiv.remove(), 3000);
            }
        }
    } catch (e) {
        console.error(e);
        alert('Lỗi kết nối'); // Keep fallback or handle similarly
    }
}

let deleteTxId = null;

function deleteTransaction(id) {
    deleteTxId = id;
    
    // Check if we have the modal in DOM
    let modalEl = document.getElementById('deleteConfirmModal');
    if (!modalEl) {
        // Create modal if not exists
        const modalHtml = `
            <div class="modal fade" id="deleteConfirmModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Xác nhận xóa</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>Bạn có chắc chắn muốn xóa giao dịch này?</p>
                            <p class="text-danger small"><i class="bi bi-exclamation-triangle"></i> Hành động này sẽ cập nhật số dư và xóa dữ liệu phân tích.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
                            <button type="button" class="btn btn-danger" onclick="confirmDeleteTransaction()">Xóa bỏ</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        modalEl = document.getElementById('deleteConfirmModal');
    }
    
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

async function confirmDeleteTransaction() {
    if (!deleteTxId) return;
    
    // Hide modal
    const modalEl = document.getElementById('deleteConfirmModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();
    
    try {
        const response = await fetch(`/api/v1/transactions/${deleteTxId}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
             if (typeof showToast === 'function') {
                showToast('Đã xóa giao dịch thành công!', 'success');
            } else {
                // Fallback if dashboard.js not loaded yet (should not happen usually)
                alert('Đã xóa giao dịch thành công!');
            }
            
            loadTransactions();
            
            if (typeof window.loadDashboardData === 'function') {
                window.loadDashboardData();
            }
        } else {
            if (typeof showToast === 'function') showToast('Lỗi khi xóa giao dịch', 'error');
            else alert('Lỗi khi xóa giao dịch');
        }
    } catch (error) {
        console.error('Error:', error);
        if (typeof showToast === 'function') showToast('Lỗi kết nối', 'error');
        else alert('Lỗi kết nối');
    }
}

async function editTransaction(id) {
    try {
        const response = await fetch(`/api/v1/transactions/${id}`);
        const data = await response.json();
        
        // Load Details
        document.getElementById('transAmount').value = parseFloat(data.amount);
        document.getElementById('transDesc').value = data.description;
        document.getElementById('transDate').value = data.date.split('T')[0];
        
        if (data.transaction_type === 'income') {
            document.getElementById('typeIncome').checked = true;
        } else {
            document.getElementById('typeExpense').checked = true;
        }
        
        // Wait for reference data
        if (wallets.length === 0) await loadReferenceData();
        
        document.getElementById('transWallet').value = data.wallet_id;
        document.getElementById('transCategory').value = data.category_id || "";
        
        // Set update mode
        editingTransactionId = id;
        document.querySelector('#addTransactionModal .modal-title').textContent = 'Cập nhật Giao dịch';
        const saveBtn = document.querySelector('#addTransactionModal .btn-primary');
        saveBtn.innerHTML = '<i class="bi bi-save"></i> Cập nhật Giao dịch';
        // Note: onclick is already set in HTML to submitTransaction()
        
        // Show Modal
        const modalEl = document.getElementById('addTransactionModal');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
        
    } catch (error) {
        console.error("Error fetching transaction details", error);
        alert('Không thể tải thông tin giao dịch');
    }
}

async function submitTransaction() {
    const typeIncome = document.getElementById('typeIncome').checked;
    const amount = document.getElementById('transAmount').value;
    const walletId = document.getElementById('transWallet').value;
    const categoryId = document.getElementById('transCategory').value;
    const date = document.getElementById('transDate').value;
    const description = document.getElementById('transDesc').value;
    
    if (!amount || !walletId) {
        alert('Vui lòng nhập số tiền và chọn ví!');
        return;
    }
    
    const payload = {
        transaction_type: typeIncome ? 'income' : 'expense',
        amount: amount,
        wallet_id: parseInt(walletId),
        category_id: categoryId ? parseInt(categoryId) : null,
        date: date,
        description: description,
        contact_person: null
    };
    
    try {
        let url = '/api/v1/transactions';
        let method = 'POST';
        
        if (editingTransactionId) {
            url = `/api/v1/transactions/${editingTransactionId}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const modalEl = document.getElementById('addTransactionModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
            
            if (typeof showToast === 'function') {
                showToast(editingTransactionId ? 'Cập nhật thành công!' : 'Tạo mới thành công!', 'success');
            } else {
                alert(editingTransactionId ? 'Cập nhật thành công!' : 'Tạo mới thành công!');
            }
            resetModal();
            loadTransactions();
            if (typeof window.loadDashboardData === 'function') {
                window.loadDashboardData();
            }
            
            // Switch to list tab if not there
            const listTabBtn = document.getElementById('list-tab');
            if (listTabBtn && !listTabBtn.classList.contains('active')) {
                listTabBtn.click();
            }
        } else {
            const err = await response.json();
            alert('Lỗi: ' + (err.message || 'Server Error'));
        }
    } catch (e) {
        console.error(e);
        alert('Lỗi kết nối');
    }
}

function resetModal() {
    const form = document.getElementById('addTransactionForm');
    if(form) form.reset();
    editingTransactionId = null;
    const title = document.querySelector('#addTransactionModal .modal-title');
    if(title) title.textContent = 'Thêm Giao dịch Mới';
    const btn = document.querySelector('#addTransactionModal .btn-primary');
    if(btn) btn.innerHTML = '<i class="bi bi-check-lg"></i> Lưu Giao dịch';
    const dateInput = document.getElementById('transDate');
    if(dateInput) dateInput.valueAsDate = new Date();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

// Upload & OCR Logic
async function processUpload() {
    const fileInput = document.getElementById('receiptFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert("Vui lòng chọn ảnh hóa đơn!");
        return;
    }
    
    const btn = document.querySelector('#uploadReceiptForm button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Đang phân tích...';
    btn.disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/v1/transactions/parse/receipt', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (result.success) {
            renderUploadResult(result.data);
        } else {
            alert('Lỗi phân tích: ' + (result.error || 'Không xác định'));
        }
    } catch (e) {
        console.error("Upload error", e);
        alert('Lỗi kết nối khi upload');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function renderUploadResult(data) {
    const resultDiv = document.getElementById('uploadResults');
    resultDiv.style.display = 'block';
    
    // Format items list if available
    let itemsHtml = '';
    if (data.items && data.items.length > 0) {
        itemsHtml = '<ul class="list-group mb-3">';
        data.items.forEach(item => {
            itemsHtml += `<li class="list-group-item d-flex justify-content-between align-items-center">
                <span>${item.desc || item.name}</span>
                <span class="badge bg-light text-dark">${formatCurrency(item.amount || 0)}</span>
            </li>`;
        });
        itemsHtml += '</ul>';
    }
    
    // Serialize data for the save button
    const txData = {
        amount: data.amount,
        description: data.raw_text || `Giao dịch tại ${data.merchant}`,
        wallet_id: data.wallet_id,
        category_id: data.category_id,
        transaction_type: 'expense', // Default to expense for receipts
        date: data.date,
        contact_person: data.merchant
    };
    // Safe stringify for HTML attribute
    const txString = JSON.stringify(txData).replace(/"/g, '&quot;');
    
    resultDiv.innerHTML = `
        <div class="card border-2 border-dark shadow-sm">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="bi bi-check-circle"></i> Kết quả phân tích</h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <p><strong>Cửa hàng:</strong> ${data.merchant || 'Không rõ'}</p>
                        <p><strong>Ngày:</strong> ${data.date ? new Date(data.date).toLocaleDateString('vi-VN') : 'Hôm nay'}</p>
                    </div>
                    <div class="col-md-6">
                         <p><strong>Tổng tiền:</strong> <span class="h4 text-success fw-bold">${formatCurrency(data.amount)}</span></p>
                         <p><strong>Danh mục gợi ý:</strong> <span class="badge bg-warning text-dark">${data.category || 'Khác'}</span></p>
                    </div>
                </div>
                
                ${itemsHtml ? '<h6>Chi tiết hóa đơn:</h6>' + itemsHtml : ''}
                
                <p class="text-muted small"><em>Mô tả tự động: ${txData.description}</em></p>
                
                <div class="d-grid gap-2">
                    <button class="btn btn-primary fw-bold" onclick="saveQuickTransaction(${txString}, this)">
                        <i class="bi bi-save"></i> Xác nhận & Lưu Giao dịch
                    </button>
                    <button class="btn btn-outline-secondary" onclick="document.getElementById('uploadResults').style.display='none'">
                        Hủy bỏ
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Scroll to results
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}
