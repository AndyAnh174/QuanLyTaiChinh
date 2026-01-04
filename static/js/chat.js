// Chat AI Logic

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    
    // Auto focus input
    userInput.focus();
    
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
            const response = await fetch('/api/v1/chat/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: message })
            });
            
            const data = await response.json();
            
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
