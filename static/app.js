const input = document.getElementById('riot-id');
const btn = document.getElementById('search-btn');
const resultsDiv = document.getElementById('results');

// Chat elements
const chatPanel = document.getElementById('chat-panel');
const chatPrompt = document.getElementById('chat-prompt');
const chatExpanded = document.getElementById('chat-expanded');
const chatMessages = document.getElementById('chat-messages');
const chatInputCompact = document.getElementById('chat-input-compact');
const chatInput = document.getElementById('chat-input');
const mainContainer = document.getElementById('main-container');
const contentArea = document.getElementById('content-area');

// Chat state
let chatHistory = [];
let isChatLoading = false;

// Champion name lookup: internal id → display name (e.g. "AurelionSol" → "Aurelion Sol")
let championNames = {};
fetch('https://ddragon.leagueoflegends.com/cdn/15.8.1/data/en_US/champion.json')
    .then(r => r.json())
    .then(json => {
        for (const champ of Object.values(json.data)) {
            championNames[champ.id] = champ.name;
        }
    })
    .catch(() => {}); // Silently fail — falls back to raw API name

// Allow pressing Enter to search
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchMatches();
});

// Allow pressing Enter to send chat messages
chatInputCompact.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendFirstMessage();
});

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function searchMatches() {
    const raw = input.value.trim();
    if (!raw) return;

    // Convert Player#TAG → Player-TAG for the API
    const riotId = raw.replace('#', '-');
    const region = document.getElementById('region').value;

    btn.disabled = true;
    resultsDiv.innerHTML = `
        <div class="status">
            <div class="spinner"></div>
            <div>Fetching matches for <strong>${escapeHtml(raw)}</strong>…</div>
        </div>`;

    // Reset chat state on new search
    resetChat();

    try {
        const res = await fetch(`/matches/${region}/${encodeURIComponent(riotId)}`);

        if (!res.ok) {
            const err = await res.json().catch(() => null);
            throw new Error(err?.detail || `Error ${res.status}`);
        }

        const json = await res.json();
        renderMatches(json);

        // Show chat panel after matches load
        showChatPanel();

        // Update URL so F5 / sharing works (keep # as %23 in URL)
        const newPath = `/search/${region}/${encodeURIComponent(raw)}`;
        if (window.location.pathname !== newPath) {
            history.pushState(null, '', newPath);
        }
    } catch (err) {
        resultsDiv.innerHTML = `<div class="status error">${escapeHtml(err.message)}</div>`;
    } finally {
        btn.disabled = false;
    }
}

function renderMatches({ source, data }) {
    if (!data || data.length === 0) {
        resultsDiv.innerHTML = '<div class="status">No matches found.</div>';
        return;
    }

    const header = `
        <div class="results-header">
            <h2>Last ${data.length} Matches</h2>
            <span>source: ${escapeHtml(source)}</span>
        </div>`;

    const cards = data.map((m) => {
        if (!m) return '';
        const outcome = m.win ? 'win' : 'loss';
        const gold = (m.gold / 1000).toFixed(1) + 'k';
        const iconUrl = `https://ddragon.leagueoflegends.com/cdn/15.8.1/img/champion/${m.champion}.png`;

        return `
        <div class="match-card ${outcome}">
            <div class="match-indicator"></div>
            <div class="match-content">
                <div class="match-champ">
                    <img class="champ-icon" src="${iconUrl}" alt="${escapeHtml(m.champion)}">
                    <div class="champ-info">
                        <span class="champ-name">${escapeHtml(championNames[m.champion] || m.champion)}</span>
                        <span class="role">${formatRole(m.role)}</span>
                    </div>
                </div>
                <div class="match-stats">
                    <div class="stat">
                        <span class="value">${escapeHtml(m.kda)}</span>
                        <span class="label">KDA</span>
                    </div>
                    <div class="stat">
                        <span class="value">${m.cs}</span>
                        <span class="label">CS</span>
                    </div>
                    <div class="stat">
                        <span class="value">${gold}</span>
                        <span class="label">Gold</span>
                    </div>
                </div>
                <div class="match-result">${outcome}</div>
            </div>
        </div>`;
    }).join('');

    resultsDiv.innerHTML = header + '<div class="match-list">' + cards + '</div>';
}

// ── Chat functions ──

function showChatPanel() {
    chatPanel.classList.add('visible');
    mainContainer.classList.add('split');
    contentArea.classList.add('split');
}

function resetChat() {
    chatHistory = [];
    chatPanel.classList.remove('visible');
    mainContainer.classList.remove('split');
    contentArea.classList.remove('split');
    chatPrompt.classList.remove('hidden');
    chatExpanded.classList.remove('active');
    chatMessages.innerHTML = '';
    chatInputCompact.value = '';
    chatInput.value = '';
}

function expandChat() {
    chatPrompt.classList.add('hidden');
    chatExpanded.classList.add('active');
    chatInput.focus();
}

function addMessage(role, content) {
    const div = document.createElement('div');
    div.className = `msg ${role}`;

    if (role === 'ai') {
        // Basic markdown-like formatting for AI responses
        div.innerHTML = formatAIMessage(content);
    } else {
        div.textContent = content;
    }

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.id = 'typing';
    div.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById('typing');
    if (el) el.remove();
}

function formatAIMessage(text) {
    // Simple markdown rendering: bold, line breaks
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

function getCurrentRiotId() {
    const raw = input.value.trim();
    return raw.replace('#', '-');
}

function getCurrentRegion() {
    return document.getElementById('region').value;
}

async function sendFirstMessage() {
    const msg = chatInputCompact.value.trim();
    if (!msg || isChatLoading) return;

    chatInputCompact.value = '';
    expandChat();
    await doSendMessage(msg);
}

async function sendMessage() {
    const msg = chatInput.value.trim();
    if (!msg || isChatLoading) return;

    chatInput.value = '';
    await doSendMessage(msg);
}

async function doSendMessage(message) {
    const riotId = getCurrentRiotId();
    const region = getCurrentRegion();

    if (!riotId) return;

    // Add user message to UI
    addMessage('user', message);

    // Show loading state
    isChatLoading = true;
    showTypingIndicator();
    setChatInputsDisabled(true);

    try {
        const res = await fetch(`/chat/${region}/${encodeURIComponent(riotId)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                history: chatHistory,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => null);
            throw new Error(err?.detail || `Error ${res.status}`);
        }

        const data = await res.json();
        removeTypingIndicator();
        addMessage('ai', data.response);

        // Save to history for multi-turn context
        chatHistory.push({ role: 'user', content: message });
        chatHistory.push({ role: 'ai', content: data.response });

    } catch (err) {
        removeTypingIndicator();
        addMessage('ai', `Error: ${err.message}`);
    } finally {
        isChatLoading = false;
        setChatInputsDisabled(false);
        chatInput.focus();
    }
}

function setChatInputsDisabled(disabled) {
    document.getElementById('chat-send').disabled = disabled;
    document.getElementById('chat-send-compact').disabled = disabled;
    chatInput.disabled = disabled;
    chatInputCompact.disabled = disabled;
}

function formatRole(role) {
    const roles = {
        'TOP': 'Top',
        'JUNGLE': 'Jungle',
        'MIDDLE': 'Mid',
        'BOTTOM': 'Bot',
        'UTILITY': 'Support',
        'Invalid': 'Fill'
    };
    return roles[role] || role;
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

// ── Auto-search from URL on page load ──
function initFromUrl() {
    const match = window.location.pathname.match(/^\/search\/([^/]+)\/(.+)$/);
    if (!match) return;

    const region = decodeURIComponent(match[1]);
    const riotId = decodeURIComponent(match[2]);

    document.getElementById('region').value = region;
    // riotId already has # (stored as %23 in URL), use as-is
    input.value = riotId;
    searchMatches();
}

window.addEventListener('popstate', initFromUrl);
initFromUrl();
