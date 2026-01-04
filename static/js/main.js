// Main JavaScript file
const API_BASE_URL = '/api/v1';

// Check access code on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAccessCode();
});

function checkAccessCode() {
    // Skip check on access code page
    if (window.location.pathname.includes('/auth/access-code')) {
        return;
    }
    
    // Check if access code is verified in session
    fetch(`${API_BASE_URL}/auth/status`)
        .then(res => res.json())
        .then(data => {
            if (!data.verified) {
                window.location.href = '/auth/access-code';
            }
        })
        .catch(err => {
            console.error('Error checking access status:', err);
        });
}

// Utility function for API calls
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (response.status === 403) {
        // Access code required
        window.location.href = '/auth/access-code';
        return null;
    }
    
    return response.json();
}

// Export for use in other scripts
window.API = {
    call: apiCall,
    baseUrl: API_BASE_URL,
};

