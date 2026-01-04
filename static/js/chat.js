// Chat AI Logic

// Track Session ID (Global Scope)
let currentSessionId = localStorage.getItem('chat_session_id') ? parseInt(localStorage.getItem('chat_session_id')) : null;

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    
    // Auto focus input
    
    // Auto focus input
    userInput.focus();


    // Load History if exists
    if (currentSessionId) {
        loadChatHistory(currentSessionId);
    }
    
    // Load Sessions list
    loadSessions();
    
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add User Message
        addMessage(message, 'user');
        userInput.value = '';
        
        // Show Typing
        showTyping(true);
        scrollToBottom();
        
        try {
            // Call API
            const payload = { 
                question: message,
                session_id: currentSessionId 
            };
            
            const response = await fetch('/api/v1/chat/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (data.session_id && currentSessionId !== data.session_id) {
                currentSessionId = data.session_id;
                // Save to localStorage
                localStorage.setItem('chat_session_id', currentSessionId);
                // Refresh sessions list to show new title
                loadSessions();
            }
            
            // Hide Typing
            showTyping(false);
            
            if (response.ok) {
                // Add AI Response
                // Format the answer (support basic markdown/formatting)
                const answer = formatAIResponse(data.answer);
                addMessage(answer, 'ai');
            } else {
                addMessage('Xin lỗi, đã có lỗi xảy ra khi kết nối với máy chủ.', 'ai');
            }
            
        } catch (error) {
            console.error(error);
            showTyping(false);
            addMessage('Xin lỗi, tôi không thể trả lời ngay bây giờ. Vui lòng thử lại sau.', 'ai');
        }
        
        scrollToBottom();
    });
});

function addMessage(content, type) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    let avatarIcon = type === 'user' ? '<i class="bi bi-person"></i>' : '<i class="bi bi-robot"></i>';
    let avatarClass = type === 'user' ? 'user-avatar' : 'ai-avatar';
    
    // Order depends on type (handled by CSS flex-direction/justify)
    // But HTML structure order matters for flex-row default
    
    let html = '';
    
    if (type === 'ai') {
        html = `
            <div class="avatar ${avatarClass}">${avatarIcon}</div>
            <div class="message-content">${content}</div>
        `;
    } else {
        // User message
        html = `
            <div class="message-content">${content}</div>
            <div class="avatar ${avatarClass}">${avatarIcon}</div>
        `;
    }
    
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
}

function showTyping(show) {
    const indicator = document.getElementById('typingIndicator');
    if (show) {
        indicator.style.display = 'block';
    } else {
        indicator.style.display = 'none';
    }
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function sendSuggestion(textOrElement) {
    let text = textOrElement;
    if (typeof textOrElement === 'object' && textOrElement.innerText) {
        text = textOrElement.innerText;
    }
    const input = document.getElementById('userInput');
    input.value = text;
    document.getElementById('chatForm').dispatchEvent(new Event('submit'));
}

function formatAIResponse(text) {
    // Use marked.js if available, otherwise fallback
    if (typeof marked !== 'undefined') {
        return marked.parse(text);
    }
    
    // Simple fallback formatter
    let formatted = text.replace(/\n/g, '<br>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return formatted;
}

// Expose sendSuggestion to window for inline onclick
window.sendSuggestion = sendSuggestion;


async function loadChatHistory(sessionId) {
    try {
        const response = await fetch(`/api/v1/chat/sessions/${sessionId}/messages`);
        if (!response.ok) return;
        
        const messages = await response.json();
        
        // Clear UI
        document.getElementById('chatMessages').innerHTML = ''; 
        
        if (messages.length === 0) {
            // If empty (shouldn't happen for valid session), show welcome
            addMessage('Xin chào! Tôi có thể giúp gì cho bạn?', 'ai');
            return;
        }
        
        messages.forEach(msg => {
            const role = msg.role === 'assistant' ? 'ai' : msg.role;
            const content = role === 'ai' ? formatAIResponse(msg.content) : msg.content;
            addMessage(content, role);
        });
        
        scrollToBottom();
        // Highlight active session
        updateActiveSessionUI(sessionId);
        
    } catch (e) {
        console.error("Error loading history", e);
    }
}

async function loadSessions() {
    try {
        const response = await fetch('/api/v1/chat/sessions');
        const sessions = await response.json();
        
        const listEl = document.getElementById('sessionList');
        if (!listEl) return;
        
        if (sessions.length === 0) {
            listEl.innerHTML = '<div class="text-center text-muted small py-3">Chưa có lịch sử.</div>';
            return;
        }
        
        // Build List
        let html = '<div class="list-group list-group-flush">';
        sessions.forEach(s => {
            const activeClass = (s.id == currentSessionId) ? 'active' : '';
            // Format time: "dd/mm HH:MM"
            const date = new Date(s.updated_at);
            const timeStr = `${date.getDate()}/${date.getMonth()+1} ${date.getHours()}:${String(date.getMinutes()).padStart(2,'0')}`;
            
            html += `
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center px-2 py-2 ${activeClass}" id="session-${s.id}" onclick="switchSession(${s.id})">
                    <div class="text-truncate" style="cursor:pointer; max-width: 170px;">
                        <div class="fw-bold text-truncate" style="font-size:0.9rem;">${s.title}</div>
                        <small class="text-muted" style="font-size:0.75rem;">${timeStr}</small>
                    </div>
                    <button class="btn btn-link btn-sm text-danger p-0" onclick="deleteSession(event, ${s.id})" title="Xóa">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            `;
        });
        html += '</div>';
        listEl.innerHTML = html;
        
    } catch(e) { console.error(e); }
}

function startNewChat() {
    localStorage.removeItem('chat_session_id');
    window.location.reload();
}

function switchSession(id) {
    if (currentSessionId === id) return;
    
    // Set ID
    currentSessionId = id;
    localStorage.setItem('chat_session_id', id);
    
    // Load
    loadChatHistory(id);
}

async function deleteSession(event, id) {
    event.stopPropagation(); // Prevent switch session
    if (!confirm('Xóa cuộc trò chuyện này?')) return;
    
    try {
        const res = await fetch(`/api/v1/chat/sessions/${id}`, { method: 'DELETE' });
        if (res.ok) {
            // Remove from UI
            loadSessions();
            
            // If deleted active session, start new
            if (id == currentSessionId) {
                startNewChat();
            }
        }
    } catch(e) { alert('Lỗi xóa session'); }
}

function updateActiveSessionUI(id) {
    // Remove active from all
    document.querySelectorAll('#sessionList .list-group-item').forEach(el => el.classList.remove('active'));
    // Add to current
    const el = document.getElementById(`session-${id}`);
    if(el) el.classList.add('active');
}
