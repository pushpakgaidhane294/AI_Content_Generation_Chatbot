
/**
 * AI Content Generation Chatbot - Frontend Application Logic (Session-based)
 */

const messageDataStore = {};
const state = {
    activeTab: 'dashboard',
    sessionId: 'session-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9),
    isGenerating: false,
    sessionsCache: [],
    currentSessionMessages: [],
    groqStatus: {
        configured: false,
        model: 'openai/gpt-oss-120b',
        message: 'Checking...'
    }
};

const elements = {
    tabs: document.querySelectorAll('.nav-btn'),
    panels: {
        dashboard: document.getElementById('view-dashboard'),
        chat: document.getElementById('view-chat'),
        history: document.getElementById('view-history'),
        about: document.getElementById('view-about')
    },
    groqPill: document.getElementById('groq-status-pill'),
    groqText: document.getElementById('groq-status-text'),
    modelName: document.getElementById('model-name'),
    offlineBanner: document.getElementById('offline-banner'),
    retrygroqBtn: document.getElementById('retry-groq-btn'),
    diagModel: document.getElementById('diag-model'),
    diagUrl: document.getElementById('diag-url'),
    diagMsg: document.getElementById('diag-msg'),
    chatForm: document.getElementById('chat-form'),
    promptInput: document.getElementById('user-prompt-input'),
    generateBtn: document.getElementById('generate-btn'),
    btnText: document.getElementById('btn-text'),
    btnSpinner: document.getElementById('btn-spinner'),
    messagesWindow: document.getElementById('chat-messages-window'),
    emptyState: document.getElementById('chat-empty-state'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    toastContainer: document.getElementById('toast-container'),
    contentType: document.getElementById('control-content-type'),
    tone: document.getElementById('control-tone'),
    audience: document.getElementById('control-audience'),
    length: document.getElementById('control-length'),
    sidebarSessionsList: document.getElementById('sidebar-sessions-list')
};

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initKeyboardShortcuts();
    checkgroqStatus();
    loadSessions();
    setInterval(checkgroqStatus, 30000);
    if (elements.retrygroqBtn) {
        elements.retrygroqBtn.addEventListener('click', () => {
            showToast('Rechecking Groq API...', 'info');
            checkgroqStatus();
        });
    }
    if (elements.clearChatBtn) {
        elements.clearChatBtn.addEventListener('click', () => {
            if (confirm('Clear current messages from screen?')) {
                startNewChat();
            }
        });
    }
});

function initNavigation() {
    elements.tabs.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(tabName) {
    if (!elements.panels[tabName]) return;
    state.activeTab = tabName;
    elements.tabs.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabName) btn.classList.add('active');
        else btn.classList.remove('active');
    });
    Object.keys(elements.panels).forEach(key => {
        if (key === tabName) {
            elements.panels[key].classList.add('active');
            elements.panels[key].style.display = 'block';
        } else {
            elements.panels[key].classList.remove('active');
            elements.panels[key].style.display = 'none';
        }
    });
}

async function checkgroqStatus() {
    try {
        const response = await fetch('/api/groq-status');
        const data = await response.json();
        state.groqStatus = data;
        updategroqUI(data);
    } catch (err) {
        console.warn('Groq status check failed:', err);
        const offlineData = {
            configured: false,
            model: 'openai/gpt-oss-120b',
            message: 'Unable to connect to Groq API. Please try again.'
        };
        state.groqStatus = offlineData;
        updategroqUI(offlineData);
    }
}

function updategroqUI(data) {
    if (!elements.groqPill) return;
    const isReady = data.configured;
    elements.groqPill.className = 'status-pill ' + (isReady ? 'connected' : 'disconnected');
    elements.groqText.textContent = isReady ? 'Configured' : 'Not Configured';
    if(elements.modelName) elements.modelName.textContent = data.model || 'openai/gpt-oss-120b';
    if (isReady && elements.offlineBanner) elements.offlineBanner.classList.add('hidden');
    else if(elements.offlineBanner) elements.offlineBanner.classList.remove('hidden');
    if (elements.diagModel) elements.diagModel.textContent = data.model || 'openai/gpt-oss-120b';
    if (elements.diagUrl) elements.diagUrl.textContent = 'https://api.groq.com/openai/v1';
    if (elements.diagMsg) elements.diagMsg.textContent = data.message;
}

function initKeyboardShortcuts() {
    if (elements.promptInput) {
        elements.promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleGenerateSubmit(e);
            }
        });
    }
}

function setGenerating(isGenerating) {
    state.isGenerating = isGenerating;
    if (elements.generateBtn) elements.generateBtn.disabled = isGenerating;
    if (elements.promptInput) elements.promptInput.disabled = isGenerating;
    if (isGenerating) {
        if(elements.btnText) elements.btnText.textContent = 'Generating...';
        if(elements.btnSpinner) elements.btnSpinner.classList.remove('hidden');
    } else {
        if(elements.btnText) elements.btnText.textContent = 'Generate';
        if(elements.btnSpinner) elements.btnSpinner.classList.add('hidden');
        if(elements.promptInput) elements.promptInput.focus();
    }
}

function startNewChat() {
    state.sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9);
    state.currentSessionMessages = [];
    clearChatWindow();
    showToast('Started a new chat session', 'info');
}

function clearChatWindow() {
    const bubbles = elements.messagesWindow.querySelectorAll('.chat-message');
    bubbles.forEach(b => b.remove());
    if (elements.emptyState) elements.emptyState.style.display = 'block';
}

function scrollToBottom() {
    if (elements.messagesWindow) {
        elements.messagesWindow.scrollTo({
            top: elements.messagesWindow.scrollHeight,
            behavior: 'smooth'
        });
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function formatTime(isoString) {
    if (!isoString) return '';
    try {
        const d = new Date(isoString);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) { return isoString; }
}

function formatCurrentTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function appendLoadingBubble(id) {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message ai loading-bubble';
    loadingDiv.id = id;
    loadingDiv.innerHTML = `
        <div class="message-header">
            <span class="message-sender">Assistant</span>
            <span>&bull; thinking...</span>
        </div>
        <div class="message-body">
            <div class="typing-indicator"><span></span><span></span><span></span></div>
        </div>
    `;
    elements.messagesWindow.appendChild(loadingDiv);
    scrollToBottom();
}

function removeLoadingBubble(id) {
    const bubble = document.getElementById(id);
    if (bubble) bubble.remove();
}

function appendUserMessage(text, messageId) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message user';
    msgDiv.id = 'user-msg-' + messageId;
    msgDiv.setAttribute('data-original-text', text);
    msgDiv.innerHTML = `
        <div class="message-header">
            <span class="message-sender">You</span>
            <span>&bull; ${formatCurrentTime()}</span>
        </div>
        <div class="message-body" id="user-msg-body-${messageId}">${escapeHtml(text)}</div>
        <div class="message-actions" style="border:none; margin-top: 5px; justify-content: flex-end;">
            <button class="action-btn edit-btn" onclick="openEditMessage(${messageId})" >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg> Edit
            </button>
        </div>
    `;
    elements.messagesWindow.appendChild(msgDiv);
    scrollToBottom();
}

window.openEditMessage = function(messageId) {
    const bodyEl = document.getElementById('user-msg-body-' + messageId);
    const currentText = bodyEl.innerText;
    bodyEl.innerHTML = `
        <textarea id="edit-textarea-${messageId}" style="width:100%; min-height:80px; padding:8px; color: black; border-radius: 4px;">${escapeHtml(currentText)}</textarea>
        <div style="display:flex; justify-content: flex-end; gap: 8px; margin-top: 8px;">
            <button onclick="cancelEdit(${messageId})" style="padding: 4px 8px; background: #ccc; border:none; border-radius:3px; color: black; cursor:pointer;">Cancel</button>
            <button onclick="saveAndRegenerate(${messageId})" style="padding: 4px 8px; background: #2563eb; border:none; border-radius:3px; color: white; cursor:pointer;">Save & Regenerate</button>
        </div>
    `;
}

window.cancelEdit = function(messageId) {
    const msgDiv = document.getElementById('user-msg-' + messageId);
    const originalText = msgDiv.getAttribute('data-original-text');
    const bodyEl = document.getElementById('user-msg-body-' + messageId);
    bodyEl.innerText = originalText;
}

window.saveAndRegenerate = async function(messageId) {
    const textarea = document.getElementById('edit-textarea-' + messageId);
    if(!textarea) return;
    const newText = textarea.value.trim();
    if(!newText) return;
    
    // Remove subsequent UI messages
    const msgDiv = document.getElementById('user-msg-' + messageId);
    while (msgDiv.nextElementSibling) {
        msgDiv.nextElementSibling.remove();
    }
    
    // Put edited text
    msgDiv.setAttribute('data-original-text', newText);
    cancelEdit(messageId);

    
    const loadingId = 'loading-' + Date.now();
    appendLoadingBubble(loadingId);
    setGenerating(true);
    
    const payload = {
        message_id: messageId,
        new_prompt: newText,
        content_type: elements.contentType.value,
        tone: elements.tone.value,
        audience: elements.audience.value,
        length: elements.length.value
    };
    
    try {
        const res = await fetch(`/api/sessions/${state.sessionId}/edit_prompt`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        removeLoadingBubble(loadingId);
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Edit generation failed.');
        }
        
        const data = await res.json();
        // data has user_message and assistant_message
        appendAiMessage(data.assistant_message);
        showToast('Message edited & regenerated!', 'success');
        loadSessions(); // refresh history
    } catch (err) {
        removeLoadingBubble(loadingId);
        showToast(err.message, 'error');
    } finally {
        setGenerating(false);
    }
}


function appendAiMessage(data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message ai';
    const msgId = 'ai-msg-' + (data.id || Date.now());
    msgDiv.id = msgId;
    messageDataStore[msgId] = data; // Store full data

    msgDiv.innerHTML = `
        <div class="message-header">
            <span class="message-sender">Assistant</span>
            <span>&bull; ${formatTime(data.created_at) || formatCurrentTime()}</span>
        </div>
        <div class="message-meta" style="margin-bottom:8px;">
            <span class="badge badge-blue">${data.content_type || 'General'}</span>
            <span class="pill">${data.tone || 'Professional'}</span>
            <span class="pill">${data.audience || 'General'}</span>
            <span class="pill">${data.length || 'Medium'}</span>
        </div>
        <div class="message-body" id="body-${msgId}">
            ${marked.parse(data.content || data.generated_response || '')}
        </div>
        <div class="message-actions">
            <button class="action-btn" onclick="executeAction('${msgId}', 'regenerate')">Regenerate</button>
            <button class="action-btn" onclick="executeAction('${msgId}', 'improve')">Improve</button>
            <button class="action-btn" onclick="executeAction('${msgId}', 'shorten')">Shorten</button>
            <button class="action-btn" onclick="executeAction('${msgId}', 'expand')">Expand</button>
            <button class="action-btn" onclick="copyContent('${msgId}')">Copy</button>
            <button class="action-btn" onclick="downloadContent('${msgId}')">Download</button>
        </div>
    `;
    elements.messagesWindow.appendChild(msgDiv);
    scrollToBottom();
}

async function handleGenerateSubmit(e) {
    if (e) e.preventDefault();
    const promptText = elements.promptInput.value.trim();
    if (!promptText) {
        showToast('Please enter a prompt before generating.', 'error');
        return false;
    }
    if (state.isGenerating) return false;

    if (!state.groqStatus.configured) {
        showToast('Groq API may not be configured properly.', 'error');
    }

    if (elements.emptyState) elements.emptyState.style.display = 'none';

    // Temporary optimistic user message, we will update its ID once response returns
    const tempId = Date.now();
    appendUserMessage(promptText, tempId);
    elements.promptInput.value = '';

    const loadingId = 'loading-' + Date.now();
    appendLoadingBubble(loadingId);
    setGenerating(true);

    const payload = {
        user_prompt: promptText,
        content_type: elements.contentType.value,
        tone: elements.tone.value,
        audience: elements.audience.value,
        length: elements.length.value,
        session_id: state.sessionId
    };

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        removeLoadingBubble(loadingId);

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Generation failed.');
        }

        const data = await response.json();
        
        // Update user message ID to real ID
        const tempMsgDiv = document.getElementById('user-msg-' + tempId);
        if(tempMsgDiv && data.user_message_id) {
            tempMsgDiv.id = 'user-msg-' + data.user_message_id;
            const btn = tempMsgDiv.querySelector('.edit-btn');
            if(btn) btn.setAttribute('onclick', `openEditMessage(${data.user_message_id})`);
            const body = tempMsgDiv.querySelector('.message-body');
            if(body) body.id = 'user-msg-body-' + data.user_message_id;
        }

        appendAiMessage(data);
        showToast('Content successfully generated!', 'success');
        
        loadSessions(); // refresh history to show new session if it was just created
        
    } catch (err) {
        removeLoadingBubble(loadingId);
        showToast(err.message || 'Generation failed.', 'error');
    } finally {
        setGenerating(false);
    }
}

window.executeAction = async function(msgId, actionType) {
    if (state.isGenerating) return;
    const msgData = messageDataStore[msgId];
    if (!msgData) {
        showToast('Message context not found.', 'error');
        return;
    }

    // We only remove messages AFTER this assistant message? 
    // Wait, actions like Regenerate/Improve just create a NEW assistant message and replace the current one? 
    // Yes! Let's just create a new AI bubble below or replace it.
    // The previous implementation appended a NEW record. Let's just append it.

    const loadingId = 'loading-' + Date.now();
    appendLoadingBubble(loadingId);
    setGenerating(true);
    showToast(`Executing ${actionType}...`, 'info');

    const payload = {
        previous_response: msgData.content || msgData.generated_response,
        user_prompt: msgData.user_prompt || 'Regenerating...',
        content_type: msgData.content_type || 'GENERAL CONTENT',
        tone: msgData.tone || 'Professional',
        audience: msgData.audience || 'General Audience',
        length: msgData.length || 'Medium',
        session_id: state.sessionId
    };

    try {
        const response = await fetch(`/api/${actionType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        removeLoadingBubble(loadingId);

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `Action ${actionType} failed.`);
        }

        const data = await response.json();
        
        // Remove old AI message, replace with new one.
        const oldMsg = document.getElementById(msgId);
        if(oldMsg) oldMsg.remove();
        
        appendAiMessage(data);
        showToast(`Action ${actionType} completed!`, 'success');
    } catch (err) {
        removeLoadingBubble(loadingId);
        showToast(err.message || `Failed to execute ${actionType}.`, 'error');
    } finally {
        setGenerating(false);
    }
}

window.copyContent = function(msgId) {
    const msgData = messageDataStore[msgId];
    if(!msgData) return;
    const text = msgData.content || msgData.generated_response;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Unable to copy to clipboard.', 'error');
    });
}

window.downloadContent = function(msgId) {
    const msgData = messageDataStore[msgId];
    if(!msgData) return;
    const text = msgData.content || msgData.generated_response;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AI_Content_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Downloaded successfully', 'success');
}

async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        if (!response.ok) return;
        const data = await response.json();
        state.sessionsCache = data.items || [];
        renderSessionsSidebar();
    } catch (err) {
        console.error('Failed to load sessions', err);
    }
}

function renderSessionsSidebar() {
    if (!elements.sidebarSessionsList) return;
    elements.sidebarSessionsList.innerHTML = '';
    
    if (state.sessionsCache.length === 0) {
        elements.sidebarSessionsList.innerHTML = '<div style="padding:1rem; text-align:center; color: var(--text-muted); font-size: 0.9rem;">No chats yet</div>';
        return;
    }

    state.sessionsCache.forEach(session => {
        const isActive = session.id === state.sessionId;
        const div = document.createElement('div');
        div.className = 'session-item';
        div.style = `
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            margin-bottom: 2px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: ${isActive ? 'var(--bg-input)' : 'transparent'};
        `;
        div.innerHTML = `
            <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem; flex: 1;" onclick="openSession('${session.id}')">
                ${escapeHtml(session.title)}
            </span>
            <button onclick="deleteSession('${session.id}', event)" class="action-btn" style="padding: 2px 4px; border: none; background: transparent; color: var(--text-muted);">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </button>
        `;
        // hover effect
        div.onmouseover = () => { if(!isActive) div.style.background = 'rgba(255,255,255,0.05)'; };
        div.onmouseout = () => { if(!isActive) div.style.background = 'transparent'; };
        
        elements.sidebarSessionsList.appendChild(div);
    });
}

window.openSession = async function(sessionId) {
    if(state.sessionId === sessionId) return;
    
    state.sessionId = sessionId;
    clearChatWindow();
    const loadingId = 'loading-' + Date.now();
    appendLoadingBubble(loadingId);
    
    try {
        const res = await fetch(`/api/sessions/${sessionId}`);
        if(!res.ok) throw new Error("Failed to load session");
        const data = await res.json();
        
        removeLoadingBubble(loadingId);
        if(elements.emptyState) elements.emptyState.style.display = 'none';
        
        data.messages.forEach(msg => {
            if(msg.role === 'user') {
                appendUserMessage(msg.content, msg.id);
            } else {
                appendAiMessage(msg);
            }
        });
        
        renderSessionsSidebar(); // highlight active
        switchTab('chat');
    } catch(e) {
        removeLoadingBubble(loadingId);
        showToast(e.message, 'error');
    }
}

window.deleteSession = async function(sessionId, e) {
    e.stopPropagation();
    if(!confirm("Delete this chat?")) return;
    
    try {
        const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
        if(!res.ok) throw new Error("Failed to delete session");
        
        showToast("Chat deleted", "success");
        if(state.sessionId === sessionId) {
            startNewChat();
        }
        loadSessions();
    } catch(e) {
        showToast(e.message, 'error');
    }
}

// Ensure the first load of app works properly
window.applySamplePrompt = function(ct, text, tone, aud, len) {
    elements.contentType.value = ct;
    elements.promptInput.value = text;
    elements.tone.value = tone;
    elements.audience.value = aud;
    elements.length.value = len;
    elements.promptInput.focus();
}

function showToast(message, type = 'info') {
    if (!elements.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
    } else if (type === 'error') {
        iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
    } else {
        iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
    }
    toast.innerHTML = `<div class="toast-icon">${iconSvg}</div><div class="toast-message">${escapeHtml(message)}</div>`;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
