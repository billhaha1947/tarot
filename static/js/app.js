// Check authentication
if (!getToken()) {
    window.location.href = '/';
}

// Global state
let socket = null;
let currentChatId = null;
let isStreaming = false;
let chats = [];

// DOM elements
const chatList = document.getElementById('chatList');
const messagesArea = document.getElementById('messagesArea');
const welcomeMessage = document.getElementById('welcomeMessage');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const sendBtnText = document.getElementById('sendBtnText');
const sendBtnSpinner = document.getElementById('sendBtnSpinner');
const newChatBtn = document.getElementById('newChatBtn');
const deleteChatBtn = document.getElementById('deleteChatBtn');
const chatTitle = document.getElementById('chatTitle');
const settingsBtn = document.getElementById('settingsBtn');
const logoutBtn = document.getElementById('logoutBtn');
const userAvatar = document.getElementById('userAvatar');
const username = document.getElementById('username');
const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
const sidebar = document.getElementById('sidebar');
const menuIcon = document.getElementById('menuIcon');

// Mobile sidebar toggle
let sidebarOpen = false;
mobileSidebarToggle.addEventListener('click', () => {
    sidebarOpen = !sidebarOpen;
    if (sidebarOpen) {
        sidebar.classList.remove('-translate-x-full');
        menuIcon.textContent = '✕';
    } else {
        sidebar.classList.add('-translate-x-full');
        menuIcon.textContent = '☰';
    }
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth < 1024 && sidebarOpen && 
        !sidebar.contains(e.target) && 
        !mobileSidebarToggle.contains(e.target)) {
        sidebar.classList.add('-translate-x-full');
        menuIcon.textContent = '☰';
        sidebarOpen = false;
    }
});

// Initialize Socket.IO
function initSocket() {
    socket = io({
        transports: ['websocket', 'polling']
    });
    
    socket.on('connect', () => {
        console.log('✓ Socket connected');
    });
    
    socket.on('disconnect', () => {
        console.log('✗ Socket disconnected');
    });
    
    socket.on('user_message', (data) => {
        console.log('User message received:', data);
    });
    
    socket.on('ai_token', (data) => {
        appendAIToken(data.content);
    });
    
    socket.on('ai_complete', (data) => {
        completeAIMessage(data);
    });
    
    socket.on('error', (data) => {
        showToast(data.message || 'Có lỗi xảy ra', 'error');
        stopStreaming();
    });
}

// Load user info
async function loadUserInfo() {
    try {
        const user = await apiRequest('/api/user');
        username.textContent = user.username;
        userAvatar.src = user.avatar;
    } catch (error) {
        showToast('Không thể tải thông tin người dùng', 'error');
    }
}

// Load chats
async function loadChats() {
    try {
        chats = await apiRequest('/api/chats');
        renderChatList();
    } catch (error) {
        showToast('Không thể tải danh sách chat', 'error');
    }
}

// Render chat list
function renderChatList() {
    if (chats.length === 0) {
        chatList.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <p>Không có cuộc trò chuyện</p>
                <p class="text-sm mt-2">Bắt đầu chat mới để khám phá Oracle</p>
            </div>
        `;
        return;
    }
    
    chatList.innerHTML = chats.map(chat => `
        <div class="chat-item glass p-3 rounded-lg cursor-pointer hover:neon-glow-cyan transition-all ${chat.id === currentChatId ? 'neon-glow-cyan' : ''}"
             data-chat-id="${chat.id}">
            <div class="flex items-start gap-3">
                <div class="text-2xl">💬</div>
                <div class="flex-1 min-w-0">
                    <h4 class="font-semibold truncate">${escapeHtml(chat.title)}</h4>
                    <p class="text-xs text-gray-400">${formatDate(chat.updated_at)}</p>
                </div>
            </div>
        </div>
    `).join('');
    
    // Add click events
    document.querySelectorAll('.chat-item').forEach(item => {
        item.addEventListener('click', () => {
            const chatId = parseInt(item.dataset.chatId);
            loadChat(chatId);
        });
    });
}

// Create new chat
async function createNewChat() {
    try {
        const chat = await apiRequest('/api/chats', {
            method: 'POST',
            body: JSON.stringify({ title: 'Cuộc trò chuyện mới' })
        });
        
        chats.unshift(chat);
        renderChatList();
        loadChat(chat.id);
        showToast('Đã tạo cuộc trò chuyện mới', 'success');
        
    } catch (error) {
        showToast('Không thể tạo chat mới', 'error');
    }
}

// Load chat
async function loadChat(chatId) {
    try {
        const chat = await apiRequest(`/api/chats/${chatId}`);
        currentChatId = chatId;
        
        chatTitle.textContent = chat.title;
        deleteChatBtn.classList.remove('hidden');
        messageInput.disabled = false;
        sendBtn.disabled = false;
        
        // Hide welcome message
        welcomeMessage.style.display = 'none';
        
        // Render messages
        messagesArea.innerHTML = '';
        chat.messages.forEach(msg => {
            if (msg.role === 'user') {
                appendUserMessage(msg.content);
            } else {
                appendAIMessage(msg.content, msg.oracle_data);
            }
        });
        
        // Scroll to bottom
        messagesArea.scrollTop = messagesArea.scrollHeight;
        
        // Update active state
        renderChatList();
        
    } catch (error) {
        showToast('Không thể tải cuộc trò chuyện', 'error');
    }
}

// Delete current chat
async function deleteCurrentChat() {
    if (!currentChatId) return;
    
    if (!confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) return;
    
    try {
        await apiRequest(`/api/chats/${currentChatId}`, {
            method: 'DELETE'
        });
        
        chats = chats.filter(c => c.id !== currentChatId);
        currentChatId = null;
        
        renderChatList();
        messagesArea.innerHTML = '';
        welcomeMessage.style.display = 'block';
        chatTitle.textContent = 'Chọn hoặc tạo cuộc trò chuyện';
        deleteChatBtn.classList.add('hidden');
        messageInput.disabled = true;
        sendBtn.disabled = true;
        
        showToast('Đã xóa cuộc trò chuyện', 'success');
        
    } catch (error) {
        showToast('Không thể xóa cuộc trò chuyện', 'error');
    }
}

// Send message
function sendMessage(message) {
    if (!currentChatId || !message.trim() || isStreaming) return;
    
    // Start streaming
    isStreaming = true;
    messageInput.disabled = true;
    sendBtn.disabled = true;
    sendBtnText.classList.add('hidden');
    sendBtnSpinner.classList.remove('hidden');
    
    // Append user message
    appendUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    
    // Create AI message placeholder
    createAIMessagePlaceholder();
    
    // Send via socket
    socket.emit('send_message', {
        token: getToken(),
        chat_id: currentChatId,
        message: message
    });
}

// Append user message
function appendUserMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-end slide-in-up';
    messageDiv.innerHTML = `
        <div class="max-w-[85%] lg:max-w-2xl">
            <div class="glass-strong rounded-2xl rounded-tr-none p-3 lg:p-4">
                <p class="text-white text-sm lg:text-base whitespace-pre-wrap break-words">${escapeHtml(content)}</p>
            </div>
            <p class="text-xs text-gray-500 mt-1 text-right">${formatTime(new Date())}</p>
        </div>
    `;
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Create AI message placeholder
function createAIMessagePlaceholder() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-start slide-in-up';
    messageDiv.id = 'ai-streaming-message';
    messageDiv.innerHTML = `
        <div class="max-w-[85%] lg:max-w-2xl">
            <div class="flex items-start gap-2 lg:gap-3">
                <div class="w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-neon-cyan to-neon-purple flex items-center justify-center text-xl lg:text-2xl flex-shrink-0">
                    🔮
                </div>
                <div class="flex-1 min-w-0">
                    <div class="glass-strong rounded-2xl rounded-tl-none p-3 lg:p-4">
                        <div class="ai-content text-sm lg:text-base break-words"></div>
                        <div class="typing-indicator mt-2">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Append AI token
function appendAIToken(token) {
    const streamingMsg = document.getElementById('ai-streaming-message');
    if (!streamingMsg) return;
    
    const contentDiv = streamingMsg.querySelector('.ai-content');
    contentDiv.textContent += token;
    
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Complete AI message
function completeAIMessage(data) {
    const streamingMsg = document.getElementById('ai-streaming-message');
    if (!streamingMsg) return;
    
    // Remove typing indicator
    const typingIndicator = streamingMsg.querySelector('.typing-indicator');
    if (typingIndicator) typingIndicator.remove();
    
    // Add Oracle card if available
    if (data.oracle_data) {
        const oracleDiv = document.createElement('div');
        oracleDiv.className = 'mt-4 glass rounded-xl p-4';
        oracleDiv.innerHTML = createOracleCard(data.oracle_data);
        streamingMsg.querySelector('.glass-strong').appendChild(oracleDiv);
    }
    
    // Add timestamp
    const timestampDiv = document.createElement('p');
    timestampDiv.className = 'text-xs text-gray-500 mt-1';
    timestampDiv.textContent = formatTime(new Date());
    streamingMsg.querySelector('.flex-1').appendChild(timestampDiv);
    
    // Remove ID
    streamingMsg.removeAttribute('id');
    
    // Stop streaming
    stopStreaming();
    
    // Reload chat list to update title
    loadChats();
}

// Append complete AI message
function appendAIMessage(content, oracleData) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-start slide-in-up';
    
    const oracleHtml = oracleData ? `
        <div class="mt-3 lg:mt-4 glass rounded-xl p-3 lg:p-4">
            ${createOracleCard(oracleData)}
        </div>
    ` : '';
    
    messageDiv.innerHTML = `
        <div class="max-w-[85%] lg:max-w-2xl">
            <div class="flex items-start gap-2 lg:gap-3">
                <div class="w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-neon-cyan to-neon-purple flex items-center justify-center text-xl lg:text-2xl flex-shrink-0">
                    🔮
                </div>
                <div class="flex-1 min-w-0">
                    <div class="glass-strong rounded-2xl rounded-tl-none p-3 lg:p-4">
                        <p class="text-white text-sm lg:text-base whitespace-pre-wrap break-words">${escapeHtml(content)}</p>
                        ${oracleHtml}
                    </div>
                    <p class="text-xs text-gray-500 mt-1">${formatTime(new Date())}</p>
                </div>
            </div>
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Create Oracle card HTML
function createOracleCard(data) {
    return `
        <div class="space-y-2 lg:space-y-3">
            <div class="flex items-center gap-2 lg:gap-3">
                <div class="text-2xl lg:text-4xl flex-shrink-0" style="text-shadow: 0 0 20px ${data.color}">
                    ${data.emoji}
                </div>
                <div class="flex-1 min-w-0">
                    <h4 class="font-bold text-sm lg:text-lg truncate" style="color: ${data.color}">
                        ${escapeHtml(data.tarot_card)}
                    </h4>
                    <p class="text-xs lg:text-sm text-gray-400 line-clamp-2">${escapeHtml(data.prediction)}</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-2 lg:gap-3">
                <div class="glass-strong rounded-lg p-2 lg:p-3">
                    <p class="text-xs text-gray-400 mb-1">May mắn</p>
                    <div class="flex items-center gap-2">
                        <div class="flex-1 bg-gray-700 rounded-full h-2 overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-neon-cyan to-neon-purple" 
                                 style="width: ${data.luck_pct}%"></div>
                        </div>
                        <span class="text-xs lg:text-sm font-bold" style="color: ${data.color}">
                            ${data.luck_pct}%
                        </span>
                    </div>
                </div>
                
                <div class="glass-strong rounded-lg p-2 lg:p-3">
                    <p class="text-xs text-gray-400 mb-1">Số may mắn</p>
                    <div class="flex flex-wrap gap-1">
                        ${data.lucky_numbers.map(n => `
                            <span class="text-xs px-1.5 lg:px-2 py-0.5 lg:py-1 rounded-full" 
                                  style="background: ${data.color}22; color: ${data.color}; border: 1px solid ${data.color}44">
                                ${n}
                            </span>
                        `).join('')}
                    </div>
                </div>
            </div>
            
            <div class="glass-strong rounded-lg p-2 lg:p-3">
                <p class="text-xs text-gray-400 mb-1">💡 Lời khuyên</p>
                <p class="text-xs lg:text-sm">${escapeHtml(data.advice)}</p>
            </div>
        </div>
    `;
}

// Stop streaming
function stopStreaming() {
    isStreaming = false;
    messageInput.disabled = false;
    sendBtn.disabled = false;
    sendBtnText.classList.remove('hidden');
    sendBtnSpinner.classList.add('hidden');
}

// Event listeners
messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

newChatBtn.addEventListener('click', createNewChat);
deleteChatBtn.addEventListener('click', deleteCurrentChat);

settingsBtn.addEventListener('click', () => {
    window.location.href = '/settings';
});

logoutBtn.addEventListener('click', () => {
    if (confirm('Bạn có chắc muốn đăng xuất?')) {
        removeToken();
        removeUser();
        window.location.href = '/';
    }
});

// Quick prompts
document.querySelectorAll('.quick-prompt').forEach(btn => {
    btn.addEventListener('click', async () => {
        if (!currentChatId) {
            await createNewChat();
        }
        messageInput.value = btn.textContent.trim().substring(2); // Remove emoji
        messageForm.dispatchEvent(new Event('submit'));
    });
});

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Vừa xong';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} phút trước`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} giờ trước`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)} ngày trước`;
    
    return date.toLocaleDateString('vi-VN');
}

function formatTime(date) {
    return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

// Typing indicator style
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #00ffff, #9d00ff);
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize app
loadUserInfo();
loadChats();
initSocket();
