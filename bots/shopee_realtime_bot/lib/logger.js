/**
 * Logger utility for Playwright bot
 * Handles file logging + console output
 */
const fs = require('fs');
const path = require('path');

const LOGS_DIR = path.join(__dirname, '..', 'logs');

// Ensure logs directory exists
if (!fs.existsSync(LOGS_DIR)) {
    fs.mkdirSync(LOGS_DIR, { recursive: true });
}

function getTimestamp() {
    return new Date().toISOString();
}

function getLogFilePath() {
    const date = new Date().toISOString().split('T')[0];
    return path.join(LOGS_DIR, `bot_${date}.log`);
}

function writeToFile(message) {
    const logPath = getLogFilePath();
    fs.appendFileSync(logPath, message + '\n');
}

const logger = {
    info: (msg, accountId = null) => {
        const prefix = accountId ? `[${accountId}]` : '[BOT]';
        const line = `${getTimestamp()} INFO ${prefix} ${msg}`;
        console.log(`✅ ${line}`);
        writeToFile(line);
    },

    warn: (msg, accountId = null) => {
        const prefix = accountId ? `[${accountId}]` : '[BOT]';
        const line = `${getTimestamp()} WARN ${prefix} ${msg}`;
        console.log(`⚠️ ${line}`);
        writeToFile(line);
    },

    error: (msg, accountId = null) => {
        const prefix = accountId ? `[${accountId}]` : '[BOT]';
        const line = `${getTimestamp()} ERROR ${prefix} ${msg}`;
        console.log(`❌ ${line}`);
        writeToFile(line);
    },

    debug: (msg, accountId = null) => {
        const prefix = accountId ? `[${accountId}]` : '[BOT]';
        const line = `${getTimestamp()} DEBUG ${prefix} ${msg}`;
        writeToFile(line);
    }
};

module.exports = logger;
