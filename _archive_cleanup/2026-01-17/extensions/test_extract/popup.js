let extractedCookies = null;

document.getElementById('extractBtn').addEventListener('click', async () => {
    const statusDiv = document.getElementById('status');
    const sendBtn = document.getElementById('sendBtn');

    try {
        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url.includes('shopee')) {
            showStatus('Please open a Shopee page first!', 'error');
            return;
        }

        // Extract cookies
        const cookies = await chrome.cookies.getAll({
            domain: '.shopee.co.id'
        });

        // Look for important cookies
        const spcEC = cookies.find(c => c.name === 'SPC_EC');
        const spcF = cookies.find(c => c.name === 'SPC_F');

        if (!spcEC || !spcF) {
            showStatus('Important cookies not found. Please login to Shopee first.', 'error');
            return;
        }

        extractedCookies = {
            SPC_EC: spcEC.value,
            SPC_F: spcF.value,
            domain: spcEC.domain,
            extracted_at: new Date().toISOString()
        };

        // Store in extension storage
        await chrome.storage.local.set({ shopee_cookies: extractedCookies });

        showStatus('✓ Cookies extracted successfully!', 'success');
        sendBtn.disabled = false;

    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
});

document.getElementById('sendBtn').addEventListener('click', async () => {
    const statusDiv = document.getElementById('status');

    try {
        if (!extractedCookies) {
            const stored = await chrome.storage.local.get('shopee_cookies');
            extractedCookies = stored.shopee_cookies;
        }

        if (!extractedCookies) {
            showStatus('No cookies to send. Extract first!', 'error');
            return;
        }

        // Send to backend
        const response = await fetch('http://localhost:8000/api/shopee-accounts/import-cookies', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Note: In production, you'd need to handle auth token
            },
            body: JSON.stringify(extractedCookies)
        });

        if (response.ok) {
            showStatus('✓ Cookies sent to dashboard successfully!', 'success');
            document.getElementById('sendBtn').disabled = true;
        } else {
            const error = await response.text();
            showStatus('Failed to send: ' + error, 'error');
        }

    } catch (error) {
        showStatus('Connection error. Make sure dashboard is running on localhost:8000', 'error');
    }
});

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = type;
    statusDiv.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
    }
}
