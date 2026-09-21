/**
 * AI Content Generation Chatbot - Frontend Application Logic
 * Vanilla JavaScript (No external frameworks)
 */

// Application State
const state = {
    activeTab: 'dashboard',
    sessionId: 'session-' + Math.random().toString(36).substring(2, 9),
    isGenerating: false,
    historyCache: [],
    selectedHistoryItem: null,
    ollamaStatus: {
        connected: false,
        model: 'llama3.2',
        message: ''
    }
};

// DOM Elements Cache
const elements = {
    tabs: document.querySelectorAll('.nav-btn'),
    panels: {
        dashboard: document.getElementById('view-dashboard'),
        chat: document.getElementById('view-chat'),
        history: document.getElementById('view-history'),
        about: document.getElementById('view-about')
    },
    ollamaPill: document.getElementById('ollama-status-pill'),
    ollamaText: document.getElementById('ollama-status-text'),
    modelName: document.getElementById('model-name'),
    offlineBanner: document.getElementById('offline-banner'),
    retryOllamaBtn: document.getElementById('retry-ollama-btn'),
    
    // Dashboard Diagnostics
    diagModel: document.getElementById('diag-model'),
    diagUrl: document.getElementById('diag-url'),
    diagMsg: document.getElementById('diag-msg'),
    cardStatusIndicator: document.getElementById('card-status-indicator'),
    
    // Chat Controls
    contentType: document.getElementById('control-content-type'),
    tone: document.getElementById('control-tone'),
    audience: document.getElementById('control-audience'),
    length: document.getElementById('control-length'),
    chatForm: document.getElementById('chat-form'),
    promptInput: document.getElementById('user-prompt-input'),
    generateBtn: document.getElementById('generate-btn'),
    btnText: document.getElementById('btn-text'),
    btnIcon: document.getElementById('btn-icon'),
    btnSpinner: document.getElementById('btn-spinner'),
    messagesWindow: document.getElementById('chat-messages-window'),
    emptyState: document.getElementById('chat-empty-state'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    
    // History
    historyContainer: document.getElementById('history-container'),
    historyCountBadge: document.getElementById('history-count-badge'),
    
    // Modal
    historyModal: document.getElementById('history-modal'),
    modalContentType: document.getElementById('modal-content-type'),
    modalTimestamp: document.getElementById('modal-timestamp'),
    modalTone: document.getElementById('modal-tone'),
    modalAudience: document.getElementById('modal-audience'),
    modalLength: document.getElementById('modal-length'),
    modalPrompt: document.getElementById('modal-prompt'),
    modalResponse: document.getElementById('modal-response'),
    
    // Toast
    toastContainer: document.getElementById('toast-container')
};

// ============================================================================
// Initialization & Lifecycle
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initKeyboardShortcuts();
    checkOllamaStatus();
    loadHistory();

    // Periodic check for Ollama status every 30 seconds
    setInterval(checkOllamaStatus, 30000);

    if (elements.retryOllamaBtn) {
        elements.retryOllamaBtn.addEventListener('click', () => {
            showToast('Rechecking Ollama daemon...', 'info');
            checkOllamaStatus();
        });
    }

    if (elements.clearChatBtn) {
        elements.clearChatBtn.addEventListener('click', clearChatScreen);
    }
});

// ============================================================================
// Navigation Management
// ============================================================================
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

    // Update button states
    elements.tabs.forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
    });

    // Update panel displays
    Object.keys(elements.panels).forEach(key => {
        elements.panels[key].classList.toggle('active', key === tabName);
    });

    // Specific tab activations
    if (tabName === 'history') {
        loadHistory();
    } else if (tabName === 'dashboard') {
        checkOllamaStatus();
    }
}

// ============================================================================
// Ollama Status Check
// ============================================================================
async function checkOllamaStatus() {
    try {
        const response = await fetch('/api/ollama-status');
        const data = await response.json();
        state.ollamaStatus = data;

        updateOllamaUI(data);
    } catch (err) {
        console.warn('Ollama status check failed:', err);
        const offlineData = {
            connected: false,
            model: 'llama3.2',
            base_url: 'http://127.0.0.1:11434',
            message: 'Ollama is not running. Please start Ollama and try again.'
        };
        state.ollamaStatus = offlineData;
        updateOllamaUI(offlineData);
    }
}

function updateOllamaUI(data) {
    if (!elements.ollamaPill) return;

    elements.ollamaPill.className = 'status-pill ' + (data.connected ? 'connected' : 'disconnected');
    elements.ollamaText.textContent = data.connected ? 'Connected' : 'Not Connected';
    elements.modelName.textContent = data.model || 'llama3.2';

    if (data.connected) {
        elements.offlineBanner.classList.add('hidden');
        if (elements.cardStatusIndicator) {
            elements.cardStatusIndicator.className = 'badge badge-green';
            elements.cardStatusIndicator.textContent = 'Active & Ready';
        }
    } else {
        elements.offlineBanner.classList.remove('hidden');
        if (elements.cardStatusIndicator) {
            elements.cardStatusIndicator.className = 'badge badge-red';
            elements.cardStatusIndicator.textContent = 'Service Offline';
        }
    }

    if (elements.diagModel) elements.diagModel.textContent = data.model;
    if (elements.diagUrl) elements.diagUrl.textContent = data.base_url || 'http://127.0.0.1:11434';
    if (elements.diagMsg) elements.diagMsg.textContent = data.message;
}

// ============================================================================
// Chatbot Interactions & Input
// ============================================================================
function initKeyboardShortcuts() {
    if (!elements.promptInput) return;

    elements.promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!state.isGenerating && elements.promptInput.value.trim()) {
                elements.chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        }
    });
}

function setGenerating(generating) {
    state.isGenerating = generating;
    elements.generateBtn.disabled = generating;

    if (generating) {
        elements.btnText.textContent = 'Generating...';
        elements.btnIcon.classList.add('hidden');
        elements.btnSpinner.classList.remove('hidden');
    } else {
        elements.btnText.textContent = 'Generate';
        elements.btnIcon.classList.remove('hidden');
        elements.btnSpinner.classList.add('hidden');
    }
}

async function handleGenerateSubmit(e) {
    if (e) e.preventDefault();

    const promptText = elements.promptInput.value.trim();
    if (!promptText) {
        showToast('Please enter a prompt before generating.', 'error');
        return false;
    }

    if (state.isGenerating) return false;

    // Check if Ollama is connected; warn user but let them try if they wish
    if (!state.ollamaStatus.connected) {
        showToast('Ollama is currently not running. Please start Ollama.', 'error');
    }

    // Hide empty state
    if (elements.emptyState) {
        elements.emptyState.style.display = 'none';
    }

    // Append User Message Bubble
    appendUserMessage(promptText);

    // Clear input
    elements.promptInput.value = '';

    // Append AI Loading Skeleton
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

        const data = await response.json();

        // Remove loading bubble
        removeLoadingBubble(loadingId);

        if (!response.ok) {
            throw new Error(data.detail || 'Generation request failed.');
        }

        // Render AI Message Bubble
        appendAiMessage(data);

        // Refresh history counter
        loadHistory();
        showToast('Content successfully generated!', 'success');

    } catch (err) {
        removeLoadingBubble(loadingId);
        appendErrorMessage(err.message || 'Error communicating with AI service.');
        showToast(err.message || 'Generation failed.', 'error');
    } finally {
        setGenerating(false);
    }

    return false;
}

// ============================================================================
// Response Action Triggers: Regenerate, Improve, Shorten, Expand
// ============================================================================
async function executeResponseAction(actionType, contextData) {
    if (state.isGenerating) return;

    const actionNames = {
        regenerate: 'Regenerating variation',
        improve: 'Polishing & improving',
        shorten: 'Condensing content',
        expand: 'Elaborating details'
    };

    showToast(`${actionNames[actionType]}...`, 'info');

    const loadingId = 'loading-' + Date.now();
    appendLoadingBubble(loadingId);
    setGenerating(true);

    let endpoint = `/api/${actionType}`;
    let payload = {};

    if (actionType === 'regenerate') {
        payload = {
            user_prompt: contextData.user_prompt,
            content_type: contextData.content_type,
            tone: contextData.tone,
            audience: contextData.audience,
            length: contextData.length,
            session_id: state.sessionId,
            previous_response: contextData.generated_response
        };
    } else {
        // Transform endpoints (improve, shorten, expand)
        payload = {
            previous_response: contextData.generated_response,
            user_prompt: contextData.user_prompt,
            content_type: contextData.content_type,
            tone: contextData.tone,
            audience: contextData.audience,
            length: contextData.length,
            session_id: state.sessionId
        };
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        removeLoadingBubble(loadingId);

        if (!response.ok) {
            throw new Error(data.detail || `Action ${actionType} failed.`);
        }

        appendAiMessage(data);
        loadHistory();
        showToast(`Action ${actionType} completed!`, 'success');

    } catch (err) {
        removeLoadingBubble(loadingId);
        appendErrorMessage(err.message || `Failed to execute ${actionType}.`);
        showToast(err.message || `Failed to execute ${actionType}.`, 'error');
    } finally {
        setGenerating(false);
    }
}

// ============================================================================
// Message DOM Rendering
// ============================================================================
function appendUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message user';
    msgDiv.innerHTML = `
        <div class="message-header">
            <span class="message-sender">You</span>
            <span>&bull; ${formatCurrentTime()}</span>
        </div>
        <div class="message-body">${escapeHtml(text)}</div>
    `;
    elements.messagesWindow.appendChild(msgDiv);
    scrollToBottom();
}

function appendAiMessage(data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message ai';

    const cleanText = data.generated_response;
    const msgId = 'ai-msg-' + (data.id || Date.now());

    msgDiv.innerHTML = `
        <div class="message-header">
            <span class="message-sender">AI Assistant (${data.model || 'llama3.2'})</span>
            <span class="badge badge-blue">${escapeHtml(data.content_type)}</span>
            <span class="pill">${escapeHtml(data.tone)}</span>
            <span class="pill">${escapeHtml(data.audience)}</span>
            <span class="pill">${escapeHtml(data.length)}</span>
            <span>&bull; ${formatTimestamp(data.created_at)}</span>
        </div>
        <div class="message-body" id="${msgId}">${escapeHtml(cleanText)}</div>
        <div class="message-actions">
            <button class="action-btn" onclick="copyTextFromElement('${msgId}', this)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                <span>Copy</span>
            </button>
            <button class="action-btn" onclick="downloadResponseText('${cleanText.replace(/'/g, "\\'")}', '${data.content_type}')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                <span>Download (.txt)</span>
            </button>
            <button class="action-btn" onclick='triggerActionFromButton("regenerate", ${JSON.stringify(data)})'>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
                <span>Regenerate</span>
            </button>
            <button class="action-btn" onclick='triggerActionFromButton("improve", ${JSON.stringify(data)})'>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                <span>Improve</span>
            </button>
            <button class="action-btn" onclick='triggerActionFromButton("shorten", ${JSON.stringify(data)})'>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/></svg>
                <span>Shorten</span>
            </button>
            <button class="action-btn" onclick='triggerActionFromButton("expand", ${JSON.stringify(data)})'>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
                <span>Expand</span>
            </button>
        </div>
    `;

    elements.messagesWindow.appendChild(msgDiv);
    scrollToBottom();
}

function triggerActionFromButton(actionType, data) {
    executeResponseAction(actionType, data);
}

function appendLoadingBubble(id) {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message ai';
    loadingDiv.id = id;
    loadingDiv.innerHTML = `
        <div class="message-header">
            <span class="message-sender">AI Assistant</span>
            <span>&bull; Thinking &amp; Generating...</span>
        </div>
        <div class="message-body">
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
            <span style="font-size:0.85rem; color:var(--text-secondary); margin-left: 8px;">
                Constructing prompt &amp; consulting local Llama 3.2...
            </span>
        </div>
    `;
    elements.messagesWindow.appendChild(loadingDiv);
    scrollToBottom();
}

function removeLoadingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function appendErrorMessage(msg) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'chat-message ai';
    errorDiv.innerHTML = `
        <div class="message-header">
            <span class="message-sender" style="color:#f87171;">System Alert</span>
        </div>
        <div class="message-body" style="background-color: var(--danger-bg); border-color: rgba(239, 68, 68, 0.4); color: #fee2e2;">
            <strong>Generation Notice:</strong> ${escapeHtml(msg)}
            <br><small style="color:#fca5a5; display:block; margin-top:4px;">Check if Ollama is running in background using command: <code>ollama run llama3.2</code></small>
        </div>
    `;
    elements.messagesWindow.appendChild(errorDiv);
    scrollToBottom();
}

function clearChatScreen() {
    elements.messagesWindow.innerHTML = '';
    if (elements.emptyState) {
        elements.emptyState.style.display = 'block';
        elements.messagesWindow.appendChild(elements.emptyState);
    }
    showToast('Chat screen cleared.', 'info');
}

function scrollToBottom() {
    elements.messagesWindow.scrollTop = elements.messagesWindow.scrollHeight;
}

// ============================================================================
// Clipboard & Download Functionality
// ============================================================================
async function copyTextFromElement(elementId, buttonEl) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const textToCopy = el.innerText || el.textContent;
    await copyText(textToCopy, buttonEl);
}

async function copyText(text, buttonEl) {
    try {
        await navigator.clipboard.writeText(text);
        if (buttonEl) {
            const originalHTML = buttonEl.innerHTML;
            buttonEl.classList.add('active-action');
            buttonEl.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                <span style="color:#34d399; font-weight:600;">Copied!</span>
            `;
            setTimeout(() => {
                buttonEl.innerHTML = originalHTML;
                buttonEl.classList.remove('active-action');
            }, 2000);
        }
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Clipboard copy error:', err);
        showToast('Unable to copy to clipboard.', 'error');
    }
}

function downloadResponseText(text, contentType) {
    try {
        const typeSlug = (contentType || 'content').toLowerCase().replace(/\s+/g, '_');
        const filename = `${typeSlug}_${new Date().toISOString().slice(0, 10)}.txt`;

        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const downloadUrl = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);

        showToast(`Downloaded as ${filename}`, 'success');
    } catch (err) {
        console.error('Download error:', err);
        showToast('Download failed.', 'error');
    }
}

// ============================================================================
// Sample Prompts Handler
// ============================================================================
function applySamplePrompt(contentType, promptText, tone, audience, length) {
    elements.contentType.value = contentType;
    elements.tone.value = tone;
    elements.audience.value = audience;
    elements.length.value = length;
    elements.promptInput.value = promptText;

    switchTab('chat');
    elements.promptInput.focus();
}

// ============================================================================
// History Management
// ============================================================================
async function loadHistory() {
    try {
        const response = await fetch('/api/history?limit=50');
        if (!response.ok) throw new Error('Failed to load history.');

        const data = await response.json();
        state.historyCache = data.items || [];

        // Update badge
        if (elements.historyCountBadge) {
            elements.historyCountBadge.textContent = data.total || 0;
        }

        renderHistory(state.historyCache);
    } catch (err) {
        console.error('History fetch error:', err);
        if (elements.historyContainer) {
            elements.historyContainer.innerHTML = `
                <div class="empty-state">
                    <p class="text-muted">Could not load history.</p>
                </div>
            `;
        }
    }
}

function renderHistory(items) {
    if (!elements.historyContainer) return;

    if (!items || items.length === 0) {
        elements.historyContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                </div>
                <h3>No History Recorded Yet</h3>
                <p>Generated responses will be saved automatically to the local SQLite database.</p>
            </div>
        `;
        return;
    }

    elements.historyContainer.innerHTML = '';

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'history-card';
        card.innerHTML = `
            <div class="history-card-header">
                <span class="badge badge-blue">${escapeHtml(item.content_type)}</span>
                <span class="text-muted text-sm">${formatTimestamp(item.created_at)}</span>
            </div>
            <div class="history-prompt-preview">${escapeHtml(item.user_prompt)}</div>
            <div class="history-response-preview">${escapeHtml(item.generated_response)}</div>
            <div class="history-card-footer">
                <div style="display:flex; gap:6px;">
                    <span class="pill">${escapeHtml(item.tone)}</span>
                    <span class="pill">${escapeHtml(item.length)}</span>
                </div>
                <div style="display:flex; gap:6px;">
                    <button class="btn btn-sm btn-outline" onclick="openHistoryItem(${item.id})">Open</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteHistoryItem(${item.id}, event)">Delete</button>
                </div>
            </div>
        `;
        elements.historyContainer.appendChild(card);
    });
}

async function deleteHistoryItem(id, event) {
    if (event) event.stopPropagation();

    if (!confirm(`Delete history entry #${id}?`)) return;

    try {
        const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete history item.');

        showToast('History item deleted.', 'success');
        loadHistory();
    } catch (err) {
        showToast(err.message || 'Error deleting item.', 'error');
    }
}

async function confirmClearAllHistory() {
    if (!state.historyCache || state.historyCache.length === 0) {
        showToast('History is already empty.', 'info');
        return;
    }

    if (!confirm('Are you sure you want to delete ALL conversation history? This cannot be undone.')) {
        return;
    }

    try {
        const res = await fetch('/api/history', { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to clear history.');

        const data = await res.json();
        showToast(`History cleared (${data.deleted_count || 0} items removed).`, 'success');
        loadHistory();
    } catch (err) {
        showToast(err.message || 'Error clearing history.', 'error');
    }
}

// ============================================================================
// History Modal
// ============================================================================
function openHistoryItem(id) {
    const item = state.historyCache.find(x => x.id === id);
    if (!item) return;

    state.selectedHistoryItem = item;

    elements.modalContentType.textContent = item.content_type;
    elements.modalTimestamp.textContent = formatTimestamp(item.created_at);
    elements.modalTone.textContent = 'Tone: ' + item.tone;
    elements.modalAudience.textContent = 'Audience: ' + item.audience;
    elements.modalLength.textContent = 'Length: ' + item.length;
    elements.modalPrompt.textContent = item.user_prompt;
    elements.modalResponse.textContent = item.generated_response;

    elements.historyModal.classList.remove('hidden');
}

function closeHistoryModal() {
    elements.historyModal.classList.add('hidden');
    state.selectedHistoryItem = null;
}

function copyModalContent() {
    if (!state.selectedHistoryItem) return;
    const btn = document.getElementById('modal-copy-btn');
    copyText(state.selectedHistoryItem.generated_response, btn);
}

function downloadModalContent() {
    if (!state.selectedHistoryItem) return;
    downloadResponseText(
        state.selectedHistoryItem.generated_response,
        state.selectedHistoryItem.content_type
    );
}

function loadHistoryIntoChat() {
    if (!state.selectedHistoryItem) return;

    const item = state.selectedHistoryItem;
    closeHistoryModal();

    // Switch to chat tab
    switchTab('chat');

    // Populate control settings
    elements.contentType.value = item.content_type;
    elements.tone.value = item.tone;
    elements.audience.value = item.audience;
    elements.length.value = item.length;

    // Render message into chat window
    if (elements.emptyState) {
        elements.emptyState.style.display = 'none';
    }

    appendUserMessage(item.user_prompt);
    appendAiMessage(item);

    showToast('Loaded into chat view.', 'info');
}

// ============================================================================
// Notification Toast System
// ============================================================================
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

    toast.innerHTML = `${iconSvg} <span>${escapeHtml(message)}</span>`;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(12px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ============================================================================
// Utilities
// ============================================================================
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatCurrentTime() {
    return new Date().toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Kolkata'
    });
}

function formatTimestamp(isoStr) {
    if (!isoStr) return formatCurrentTime();
    try {
        const d = new Date(isoStr);
        return d.toLocaleDateString('en-IN', {
            month: 'short',
            day: 'numeric',
            timeZone: 'Asia/Kolkata'
        }) + ' ' + d.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'Asia/Kolkata'
        });
    } catch {
        return isoStr;
    }
}
