/**
 * API Uploader - Sends scraped data to backend
 */
const axios = require('axios');
const logger = require('./logger');

const API_BASE = process.env.API_BASE || 'http://localhost:8000/api';
const ACCESS_CODE = process.env.ACCESS_CODE || '';

async function postSnapshot(payload) {
    const url = `${API_BASE}/bot/realtime-snapshots/ingest`;

    logger.debug(`POST ${url}`, payload.shopee_account_id);

    try {
        const response = await axios.post(url, payload, {
            headers: {
                'Content-Type': 'application/json',
                'X-Access-Code': ACCESS_CODE
            },
            timeout: 10000
        });

        logger.info(`Snapshot ingested: ${response.data.snapshot_id}`, payload.shopee_account_id);
        return { success: true, data: response.data };

    } catch (error) {
        const msg = error.response?.data?.detail || error.message;
        logger.error(`Ingest failed: ${msg}`, payload.shopee_account_id);
        return { success: false, error: msg };
    }
}

async function postBatchSnapshots(snapshots) {
    const url = `${API_BASE}/bot/realtime-snapshots/ingest-batch`;

    try {
        const response = await axios.post(url, { snapshots }, {
            headers: {
                'Content-Type': 'application/json',
                'X-Access-Code': ACCESS_CODE
            },
            timeout: 30000
        });

        logger.info(`Batch ingested: ${response.data.ingested}/${response.data.total}`);
        return { success: true, data: response.data };

    } catch (error) {
        logger.error(`Batch ingest failed: ${error.message}`);
        return { success: false, error: error.message };
    }
}

module.exports = { postSnapshot, postBatchSnapshots };
