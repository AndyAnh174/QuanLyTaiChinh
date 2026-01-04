// Chat AI Logic

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    
    // Track Session ID
    let currentSessionId = localStorage.getItem('chat_session_id') ? parseInt(localStorage.getItem('chat_session_id')) : null;
    
    // Auto focus input
    userInput.focus();

    // Load History if exists
    if (currentSessionId) {
        loadChatHistory(currentSessionId);
    }
    
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
            
            // Provide Feedback if session created
            if (data.session_id && currentSessionId !== data.session_id) {
                currentSessionId = data.session_id;
                // Optional: Save to localStorage to persist across refreshes if desired
                localStorage.setItem('chat_session_id', currentSessionId);
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
        if (messages.length === 0) return;
        
        // Clear default welcome message if we have history (optional, or append)
        // For now, let's keep welcome message but maybe clear it if there's a lot of history
        // document.getElementById('chatMessages').innerHTML = ''; 
        
        messages.forEach(msg => {
            const role = msg.role === 'assistant' ? 'ai' : msg.role;
            // Only format if AI
            const content = role === 'ai' ? formatAIResponse(msg.content) : msg.content;
            addMessage(content, role);
        });
        
        scrollToBottom();
        
    } catch (e) {
        console.error("Error loading history", e);
    }
}
