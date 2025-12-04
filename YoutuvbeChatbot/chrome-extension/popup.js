document.addEventListener('DOMContentLoaded', function () {
    const status = document.getElementById('status');
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        const currentTab = tabs[0];
        if (currentTab.url && currentTab.url.includes('youtube.com/watch')) {
            status.textContent = 'Active on YouTube video page!';
            status.classList.add('active');
        } else {
            status.textContent='Navigate to a YouTube video to use the assistant';
        
        }
    });
});
