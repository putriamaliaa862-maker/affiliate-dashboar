// Popup JavaScript
document.addEventListener('DOMContentLoaded', () => {
    loadStatus();

    document.getElementById('syncNow').addEventListener('click', handleSyncNow);
    document.getElementById('openSettings').addEventListener('click', handleOpenSettings);

    // Refresh status every 5 seconds
    setInterval(loadStatus, 5000);
});

function loadStatus() {
    chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
        if (!response) {
            updateStatus(false);
            return;
        }

        updateStatus(response.connected);

        // Update last sync
        if (response.lastSync) {
            const lastSyncDate = new Date(response.lastSync);
            const now = new Date();
            const diffMinutes = Math.floor((now - lastSyncDate) / 60000);

            if (diffMinutes < 1) {
                document.getElementById('lastSync').textContent = 'Just now';
            } else if (diffMinutes < 60) {
                document.getElementById('lastSync').textContent = `${diffMinutes}m ago`;
            } else {
                const diffHours = Math.floor(diffMinutes / 60);
                document.getElementById('lastSync').textContent = `${diffHours}h ago`;
            }
        }

        // Update total synced
        document.getElementById('totalSynced').textContent = response.totalSynced || 0;

        // Update API endpoint
        const endpoint = response.apiEndpoint || 'Not configured';
        document.getElementById('apiEndpoint').textContent =
            endpoint.length > 30 ? endpoint.substring(0, 30) + '...' : endpoint;
    });
}

function updateStatus(connected) {
    const statusElement = document.getElementById('status');
    const statusText = statusElement.querySelector('.status-text');

    if (connected) {
        statusElement.classList.remove('disconnected');
        statusText.textContent = 'Connected';
    } else {
        statusElement.classList.add('disconnected');
        statusText.textContent = 'Disconnected';
    }
}

function handleSyncNow() {
    const button = document.getElementById('syncNow');
    button.disabled = true;
    button.textContent = '🔄 Syncing...';

    chrome.runtime.sendMessage({ type: 'MANUAL_SYNC' }, (response) => {
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = '<span class="btn-icon">🔄</span> Sync Now';

            if (response && response.success) {
                showMessage('✓ Sync started');
            } else {
                showMessage('✗ Sync failed');
            }
        }, 1000);
    });
}

function handleOpenSettings() {
    chrome.runtime.openOptionsPage();
}

function showMessage(text) {
    // Create temporary message
    const message = document.createElement('div');
    message.textContent = text;
    message.style.cssText = `
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: #333;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
    z-index: 1000;
  `;

    document.body.appendChild(message);
    setTimeout(() => message.remove(), 2000);
}
