// Options Page JavaScript
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();

    document.getElementById('settingsForm').addEventListener('submit', saveSettings);
});

function loadSettings() {
    chrome.storage.local.get(['apiEndpoint', 'syncInterval', 'syncApiKey', 'autoSync'], (result) => {
        if (result.apiEndpoint) {
            document.getElementById('apiEndpoint').value = result.apiEndpoint;
        }
        if (result.syncInterval) {
            document.getElementById('syncInterval').value = result.syncInterval / 60000; // Convert ms to minutes
        }
        if (result.syncApiKey) {
            document.getElementById('syncApiKey').value = result.syncApiKey;
        }
        if (result.autoSync !== undefined) {
            document.getElementById('autoSync').checked = result.autoSync;
        }
    });
}

function saveSettings(e) {
    e.preventDefault();

    const settings = {
        apiEndpoint: document.getElementById('apiEndpoint').value,
        syncInterval: parseInt(document.getElementById('syncInterval').value) * 60000, // Convert minutes to ms
        syncApiKey: document.getElementById('syncApiKey').value,
        autoSync: document.getElementById('autoSync').checked
    };

    chrome.storage.local.set(settings, () => {
        // Show success message
        const message = document.getElementById('successMessage');
        message.classList.add('show');

        setTimeout(() => {
            message.classList.remove('show');
        }, 3000);

        // Notify background script to reload settings
        chrome.runtime.sendMessage({ type: 'SETTINGS_UPDATED', settings });
    });
}
