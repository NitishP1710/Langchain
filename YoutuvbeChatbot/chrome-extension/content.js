(function () {
    'use strict';

    let chatContainer = null;
    let isChatVisible = false;

    // Wait for YouTube page to load and ensure user interaction before any initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            // Delay initialization to avoid automatic triggering
            setTimeout(() => initChat(), 1000);
        });
    } else {
        // Delay initialization to avoid automatic triggering  
        setTimeout(() => initChat(), 1000);
    }

    function initChat() {
        if (!window.location.href.includes('youtube.com/watch')) {
            return;
        }
        const urlParams = new URLSearchParams(window.location.search);
        const videoId = urlParams.get('v');//in youtube url v used for query params
        if (!videoId) {
            console.error('Could not extract video ID from URL');
            return;
        }
        addToggleButton();
    }

    function createChatContainer(videoId) {
        const existingChat = document.getElementById('youtube-ai-chat');
        if (existingChat) {
            existingChat.remove();
        }
        chatContainer = document.createElement('div');
        chatContainer.id = 'youtube-ai-chat';
        chatContainer.innerHTML = `
      <div class="chat-header">
        <h3>🤖 AI Video Assistant</h3>
        <button class="close-btn" id="chat-close-btn">×</button>
      </div>
      <div class="chat-body" id="chat-body">
        <div class="loading" id="chat-loading">Analyzing video content...</div>
      </div>
      <div class="chat-input-container">
        <input type="text" id="chat-input" placeholder="Ask questions about this video...">
        <button id="chat-send">Send</button>
      </div>
    `;
        document.body.appendChild(chatContainer);
        setupEventListeners(videoId);
        // Show a manual initialization prompt instead of auto-initializing
        showInitializationPrompt(videoId);
    }

    function setupEventListeners(videoId) {
        const closeBtn = document.getElementById('chat-close-btn');
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('chat-send');

        closeBtn.addEventListener('click', () => {
            chatContainer.style.display = 'none';
            isChatVisible = false;
        });

        sendBtn.addEventListener('click', (event) => {
            event.preventDefault();
            sendMessage(videoId);
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage(videoId);
            }
        });

        // Don't auto-initialize to avoid storage access issues
        // Manual initialization will be triggered by button click
    }

    function showInitializationPrompt(videoId) {
        const chatBody = document.getElementById('chat-body');
        chatBody.innerHTML = `
            <div class="initialization-prompt">
                <h4>🤖 AI Video Assistant Ready!</h4>
                <p>Click the button below to analyze this video and start chatting.</p>
                <button id="init-chat-btn" class="init-btn">Analyze Video Content</button>
                <div class="loading" id="chat-loading" style="display: none;">Analyzing video content...</div>
            </div>
        `;

        // Add click handler for manual initialization
        document.getElementById('init-chat-btn').addEventListener('click', (event) => {
            event.preventDefault();
            initializeChatWithVideo(videoId);
        });
    }

    function initializeChatWithVideo(videoId) {
        const chatBody = document.getElementById('chat-body');
        const loading = document.getElementById('chat-loading');

        // Show loading state
        loading.style.display = "block";
        loading.textContent = "Analyzing video content...";

        // Check if running in Chrome extension context and ensure user gesture
        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
            // Use Chrome extension messaging for backend communication
            chrome.runtime.sendMessage({
                action: 'initializeChat',
                video_id: videoId

            }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error('Chrome extension error:', chrome.runtime.lastError);
                    loading.textContent = 'Error connecting to AI service. Please try again.';
                    return;
                }

                if (response && response.success) {
                    // Wait for video processing to complete before showing ready message
                    waitForVideoProcessing(videoId);
                } else {
                    loading.textContent = 'Error initializing chat: ' + (response.error || 'Unknown error');
                }
            });
        } else {
            // No fallback - Chrome extension only
            loading.textContent = 'Chrome extension required. Please reload extension.';
        }
    }

    function waitForVideoProcessing(videoId) {
        const loading = document.getElementById('chat-loading');
        const checkInterval = setInterval(() => {
            // Check video processing status via Chrome messaging
            if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
                chrome.runtime.sendMessage({
                    action: 'checkVideoStatus',
                    video_id: videoId
                }, (response) => {
                    if (chrome.runtime.lastError) {
                        console.error('Chrome extension error:', chrome.runtime.lastError);
                        clearInterval(checkInterval);
                        return;
                    }

                    if (response && response.success && response.status === 'ready') {
                        clearInterval(checkInterval);
                        loading.style.display = 'none';
                        addMessage('AI Assistant', 'Great! I\'ve analyzed this video. Ask me anything about its content!', 'bot');
                    }
                });
            } else {
                // Fallback using chrome extension only - no direct fetch
                const testInterval = setInterval(() => {
                    // Try Chrome messaging again
                    chrome.runtime.sendMessage({
                        action: 'checkVideoStatus',
                        video_id: videoId
                    }, (response) => {
                        if (response && response.success && response.status === 'ready') {
                            clearInterval(checkInterval);
                            clearInterval(testInterval);
                            loading.style.display = 'none';
                            addMessage('AI Assistant', 'Great! I\'ve analyzed this video. Ask me anything about its content!', 'bot');
                        }
                    });
                }, 1000);
            }
        }, 2000); // Check every 2 seconds

        // Timeout after 30 seconds
        setTimeout(() => {
            clearInterval(checkInterval);
            loading.textContent = 'Video analysis taking longer than expected. Please try again.';
        }, 30000);
    }

    function sendMessage(videoId) {
        const input = document.getElementById('chat-input');
        const question = input.value.trim();
        if (!question) return;
        addMessage('You', question, 'user');
        input.value = '';

        // Show typing indicator
        const chatBody = document.getElementById('chat-body');
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot typing-indicator';
        typingIndicator.innerHTML = '<span>AI is thinking...</span>';
        chatBody.appendChild(typingIndicator);
        chatBody.scrollTop = chatBody.scrollHeight;

        // Check if running in Chrome extension context
        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
            // Use Chrome extension messaging for backend communication
            chrome.runtime.sendMessage({
                action: 'askQuestion',
                video_id: videoId,
                question: question
            }, (response) => {
                typingIndicator.remove();
                if (chrome.runtime.lastError) {
                    console.error('Chrome extension error:', chrome.runtime.lastError);
                    addMessage('AI Assistant', 'Sorry, I encountered an error. Please try again.', 'bot error');
                    return;
                }
                if (response && response.success) {
                    addMessage('AI Assistant', response.answer, 'bot');
                } else {
                    addMessage('AI Assistant', 'Sorry, I encountered an error. Please try again.', 'bot error');
                }
            });
        } else {
            // No fallback - Chrome extension only
            typingIndicator.remove();
            addMessage('AI Assistant', 'Chrome extension required. Please reload extension.', 'bot error');
        }
    }

    function addMessage(sender, text, type) {
        const chatBody = document.getElementById('chat-body');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        messageDiv.innerHTML = `
      <div class="message-header">${sender}</div>
      <div class="message-text">${text}</div>
    `;

        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function addToggleButton() {
        const existingToggle = document.getElementById('ai-chat-toggle');
        if (existingToggle) {
            existingToggle.remove();
        }

        const toggleButton = document.createElement('button');
        toggleButton.id = 'ai-chat-toggle';
        toggleButton.innerHTML = '🤖';
        toggleButton.title = 'Open AI Chat Assistant';
        toggleButton.className = 'ai-toggle-btn';

        // Position near the subscribe button
        const subscribeButton = document.querySelector('#subscribe-button') ||
            document.querySelector('[id*="subscribe"]') ||
            document.querySelector('.ytd-subscribe-button-renderer');

        if (subscribeButton) {
            subscribeButton.parentElement.insertBefore(toggleButton, subscribeButton.nextSibling);
        } else {
            // Fallback positioning
            const playerContainer = document.querySelector('#columns') || document.querySelector('#secondary');
            if (playerContainer) {
                playerContainer.insertBefore(toggleButton, playerContainer.firstChild);
            }
        }

        toggleButton.addEventListener('click', (event) => {
            event.preventDefault();
            if (!chatContainer) {
                const urlParams = new URLSearchParams(window.location.search);
                const videoId = urlParams.get('v');
                if (videoId) {
                    createChatContainer(videoId);
                } else {
                    console.error('Could not extract video ID from URL');
                    return;
                }
            }

            chatContainer.style.display = isChatVisible ? 'none' : 'flex';
            isChatVisible = !isChatVisible;

            if (isChatVisible) {
                toggleButton.innerHTML = '🤖⚡';
            } else {
                toggleButton.innerHTML = '🤖';
            }
        });
    }

})();
