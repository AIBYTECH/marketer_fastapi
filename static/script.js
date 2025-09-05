class MarketerChat {
    constructor() {
        this.currentChatId = null;
        this.chatHistories = [];
        this.initializeEventListeners();
        this.loadChatHistory();
    }

    initializeEventListeners() {
        // Send button click
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key press in input
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // New chat button
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.createNewChat();
        });
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Disable input and send button
        input.disabled = true;
        document.getElementById('sendBtn').disabled = true;

        // Add user message to chat
        this.addMessageToChat('user', message);
        input.value = '';

        // Show loading indicator
        this.showLoading(true);

        try {
            // Send message to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    chat_id: this.currentChatId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update current chat ID
            this.currentChatId = data.chat_id;
            
            // Add assistant response to chat
            this.addMessageToChat('assistant', data.response);
            
            // Update chat history in sidebar
            this.updateChatHistory();

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToChat('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            // Re-enable input and send button
            input.disabled = false;
            document.getElementById('sendBtn').disabled = false;
            this.showLoading(false);
        }
    }

    addMessageToChat(role, content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async createNewChat() {
        try {
            const response = await fetch('/api/chat/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.currentChatId = data.chat_id;

            // Clear current chat display
            this.clearChatDisplay();

            // Add welcome message
            this.addMessageToChat('assistant', 'Hello, I am your digital marketing assistant. How can I assist you today?');

            // Update chat history
            this.updateChatHistory();

        } catch (error) {
            console.error('Error creating new chat:', error);
            alert('Failed to create new chat. Please try again.');
        }
    }

    clearChatDisplay() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.chatHistories = data.chats;
            this.renderChatHistory();

        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    renderChatHistory() {
        const chatList = document.getElementById('chatList');
        chatList.innerHTML = '';

        this.chatHistories.forEach((chat, index) => {
            const chatItem = document.createElement('button');
            chatItem.className = 'chat-item';
            chatItem.textContent = `Chat ${index + 1}`;
            chatItem.addEventListener('click', () => {
                this.loadChat(chat.chat_id);
            });
            chatList.appendChild(chatItem);
        });
    }

    async loadChat(chatId) {
        try {
            const response = await fetch(`/api/chat/${chatId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.currentChatId = chatId;

            // Clear current chat display
            this.clearChatDisplay();

            // Load messages
            data.messages.forEach(message => {
                this.addMessageToChat(message.role, message.content);
            });

            // Update active chat in sidebar
            this.updateActiveChat(chatId);

        } catch (error) {
            console.error('Error loading chat:', error);
            alert('Failed to load chat. Please try again.');
        }
    }

    updateActiveChat(chatId) {
        const chatItems = document.querySelectorAll('.chat-item');
        chatItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // Find and highlight the active chat
        const activeIndex = this.chatHistories.findIndex(chat => chat.chat_id === chatId);
        if (activeIndex !== -1) {
            chatItems[activeIndex].classList.add('active');
        }
    }

    async updateChatHistory() {
        await this.loadChatHistory();
        if (this.currentChatId) {
            this.updateActiveChat(this.currentChatId);
        }
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = show ? 'flex' : 'none';
    }
}

// Initialize the chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new MarketerChat();
});
