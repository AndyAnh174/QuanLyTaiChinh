// Access Code Authentication
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('accessCodeForm');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    
    // Check if already verified
    checkAccessStatus();
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const code = document.getElementById('accessCode').value;
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
        
        try {
            const response = await fetch('/api/v1/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                successMessage.textContent = data.message || 'Xác nhận thành công! Đang chuyển hướng...';
                successMessage.style.display = 'block';
                
                // Store verification in localStorage
                localStorage.setItem('access_code_verified', 'true');
                
                // Redirect to dashboard after 1 second
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                errorMessage.textContent = data.error || 'Mã truy cập không đúng';
                errorMessage.style.display = 'block';
                
                if (data.attempts_remaining !== undefined) {
                    errorMessage.textContent += ` (Còn ${data.attempts_remaining} lần thử)`;
                }
            }
        } catch (error) {
            errorMessage.textContent = 'Lỗi kết nối. Vui lòng thử lại.';
            errorMessage.style.display = 'block';
        }
    });
});

function checkAccessStatus() {
    // Check localStorage first
    if (localStorage.getItem('access_code_verified') === 'true') {
        // Verify with server
        fetch('/api/v1/auth/status')
            .then(res => res.json())
            .then(data => {
                if (data.verified) {
                    window.location.href = '/dashboard';
                } else {
                    localStorage.removeItem('access_code_verified');
                }
            });
    }
}

