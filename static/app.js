// Simple frontend - stores chat history in localStorage and calls /api/chat
div.className = m.role === 'ai' ? 'msg ai' : 'msg human';
div.textContent = m.content;
messagesEl.appendChild(div);
});
messagesEl.scrollTop = messagesEl.scrollHeight;
}


function appendAI(text) {
    chatHistory.push({ role: 'ai', content: text });
    save();
    renderMessages();
}
function appendHuman(text) {
    chatHistory.push({ role: 'human', content: text });
    save();
    renderMessages();
}


function save() {
    localStorage.setItem('chat_history', JSON.stringify(chatHistory));
    localStorage.setItem('chat_histories', JSON.stringify(pastConversations));
}


form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendHuman(text);
    input.value = '';


    // Build a simple serializable history for the API (role/content only)
    const payloadHistory = chatHistory.map(h => ({ role: h.role, content: h.content }));


    const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: payloadHistory })
    });


    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
        appendAI('Error: ' + (err.detail || 'Server error'));
        return;
    }


    const data = await res.json();
    appendAI(data.reply);
});


newChatBtn.addEventListener('click', () => {
    if (chatHistory.length) {
        pastConversations.push(chatHistory);
    }
    chatHistory = [];
    save();
    renderHistory();
    renderMessages();
});


function renderHistory() {
    historyList.innerHTML = '';
    pastConversations.forEach((h, i) => {
        const btn = document.createElement('button');
        btn.textContent = `Chat ${i + 1}`;
        btn.addEventListener('click', () => {
            chatHistory = h;
            save();
            renderMessages();
        });
        historyList.appendChild(btn);
    });
}


// initial render
renderHistory();
renderMessages();