
console.log('YouTube AI Chat Assistant background script loaded');

chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed');
});
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('youtube.com/watch')) {
        console.log('YouTube video page loaded, ready for chat assistant');
    }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractVideoId') {
        const videoId = extractVideoIdFromUrl(sender.tab.url);
        sendResponse({ videoId: videoId });
    } else if (request.action === 'initializeChat') {
        initializeChat(request.video_id, sendResponse);
        return true;
    } else if (request.action === 'askQuestion') {
        askQuestion(request.video_id, request.question, sendResponse);
        return true;
    } else if (request.action === 'checkVideoStatus') {
        checkVideoStatus(request.video_id, sendResponse);
        return true;
    }
});


async function initializeChat(videoId, sendResponse) {
    try {
        console.log('Initializing chat for video:', videoId);

        const response = await fetch('http://localhost:5000/initialize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ video_id: videoId })
        });

        const data = await response.json();

        if (response.ok) {
            sendResponse({ success: true, data: data });
        } else {
            sendResponse({ success: false, error: data.error || 'Unknown error' });
        }
    } catch (error) {
        console.error('Error initializing chat:', error);
        sendResponse({ success: false, error: error.message });
    }
}

// Send question to backend in background context
async function askQuestion(videoId, question, sendResponse) {
    try {
        console.log('Asking question for video:', videoId);

        const response = await fetch('http://localhost:5000/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                video_id: videoId,
                question: question
            })
        });

        const data = await response.json();

        if (response.ok) {
            sendResponse({ success: true, answer: data.answer });
        } else {
            sendResponse({ success: false, error: data.answer || data.error || 'Unknown error' });
        }
    } catch (error) {
        console.error('Error asking question:', error);
        sendResponse({ success: false, error: error.message });
    }
}

// Check video processing status
async function checkVideoStatus(videoId, sendResponse) {
    try {
        console.log('Checking video status for:', videoId);

        const response = await fetch('http://localhost:5000/status/' + videoId);
        const data = await response.json();

        if (response.ok) {
            sendResponse({ success: true, status: data.status, data: data });
        } else {
            sendResponse({ success: false, error: data.error || 'Unknown error' });
        }
    } catch (error) {
        console.error('Error checking video status:', error);
        sendResponse({ success: false, error: error.message });
    }
}

function extractVideoIdFromUrl(url) {
    const urlParams = new URLSearchParams(url.split('?')[1]);
    return urlParams.get('v');
}
