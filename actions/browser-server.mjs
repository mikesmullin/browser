#!/usr/bin/env node

/*
 * Browser Debug Server - Interactive Playwright Browser Session
 *
 * This script launches a Playwright browser in headed mode and provides
 * an HTTP API for interactive debugging and development.
 *
 * Usage:
 *   node actions/browser-server.mjs
 *
 * Server runs on http://localhost:3001
 * Browser opens in headed mode for visual debugging
 */

import { chromium } from 'playwright';
import http from 'http';
import url from 'url';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Configuration
const MOCK_MODE = process.argv.includes('--mock') || process.env.BROWSER_MOCK === 'true';
const SESSION_CACHE_FILE = 'storage/.session-cache.json';

// Get current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '..');
const SESSION_CACHE_PATH = path.join(PROJECT_ROOT, SESSION_CACHE_FILE);

// Load credentials from environment variables (optional)
const username = process.env.MYUSER;
const password = process.env.MYPW;

if (MOCK_MODE) {
    console.log('🎭 Mock mode: Using dummy credentials');
} else if (username && password) {
    console.log(`🔐 Using credentials for: ${username}`);
} else {
    console.log('ℹ️  No credentials provided - browser will use default authentication');
}

console.log(`🔐 Using credentials for: ${username || 'no-auth'}`);

// Global browser state
let browser = null;
let context = null;
let page = null;
let consoleLogs = [];

// Mock browser state for testing
let mockState = {
    url: 'about:blank',
    title: 'Mock Browser Page',
    ready: false
};

/**
 * Load existing session from cache file
 */
function loadSessionCache() {
    try {
        if (fs.existsSync(SESSION_CACHE_PATH)) {
            const cacheData = JSON.parse(fs.readFileSync(SESSION_CACHE_PATH, 'utf-8'));
            console.log('📂 Loaded session cache from file');
            return cacheData;
        }
    } catch (error) {
        console.warn('⚠️  Failed to load session cache:', error.message);
    }
    return null;
}

/**
 * Clear session cache file (used when session is invalid/expired)
 */
function clearSessionCache() {
    try {
        if (fs.existsSync(SESSION_CACHE_PATH)) {
            fs.unlinkSync(SESSION_CACHE_PATH);
            console.log('🧹 Cleared session cache file');
            return true;
        }
    } catch (error) {
        console.warn('⚠️  Failed to clear session cache:', error.message);
    }
    return false;
}

/**
 * Check if error indicates session timeout/closure
 */
function isSessionTimeoutError(error) {
    const timeoutPatterns = [
        'Target page, context or browser has been closed',
        'Target closed',
        'Page has been closed',
        'Browser has been closed',
        'Context has been closed'
    ];
    
    return timeoutPatterns.some(pattern => 
        error.message && error.message.includes(pattern)
    );
}

/**
 * Save session to cache file
 */
function saveSessionCache(storageState) {
    try {
        // Ensure storage directory exists
        const storageDir = path.dirname(SESSION_CACHE_PATH);
        if (!fs.existsSync(storageDir)) {
            fs.mkdirSync(storageDir, { recursive: true });
        }

        fs.writeFileSync(SESSION_CACHE_PATH, JSON.stringify(storageState, null, 2));
        console.log('💾 Saved session cache to file');
    } catch (error) {
        console.error('❌ Failed to save session cache:', error.message);
    }
}

/**
 * Save current session state
 */
async function saveCurrentSession() {
    if (MOCK_MODE || !context) return;

    try {
        const storageState = await context.storageState();
        saveSessionCache(storageState);
    } catch (error) {
        console.warn('⚠️  Failed to save current session:', error.message);
    }
}

// Start Playwright browser or mock
async function initializeBrowser() {
    if (MOCK_MODE) {
        console.log('🎭 Starting in MOCK mode (no real browser)...');

        // Simulate browser initialization delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        mockState.ready = true;
        mockState.url = 'https://mock.example.com';
        mockState.title = 'Mock Browser Debug Page';

        console.log('✅ Mock browser initialized and ready');
        return;
    }

    console.log('🚀 Starting Playwright browser...');

    // Check if we should run in headless mode (headed is default for visual debugging)
    const isHeadless = process.argv.includes('--headless') || process.env.BROWSER_HEADLESS === 'true';

    browser = await chromium.launch({
        headless: isHeadless,  // Default to headed for visual debugging
        // slowMo: !isHeadless ? 100 : 0,      // Slight delay for visual debugging
        args: [
            '--disable-web-security',
            // '--disable-features=VizDisplayCompositor',
            // '--auth-server-whitelist=*.corp.yourco.net',
            // '--auth-negotiate-delegate-whitelist=*.corp.yourco.net'
        ]
    });

    context = await browser.newContext({
        httpCredentials: username && password ? {
            username: username,
            password: password
        } : undefined,
        ignoreHTTPSErrors: true,
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
    });

    // Load existing session if available
    const existingSession = loadSessionCache();
    if (existingSession) {
        console.log('📂 Restoring previous session...');
        try {
            await context.addCookies(existingSession.cookies || []);
        } catch (error) {
            console.warn('⚠️  Failed to restore session, clearing cache:', error.message);
            clearSessionCache();
        }
    }

    page = await context.newPage();

    // Capture console logs
    page.on('console', msg => {
        const logEntry = {
            type: msg.type(),
            text: msg.text(),
            timestamp: new Date().toISOString()
        };
        consoleLogs.push(logEntry);

        // Keep only last 100 logs
        if (consoleLogs.length > 100) {
            consoleLogs = consoleLogs.slice(-100);
        }

        console.log(`📝 Console [${msg.type()}]: ${msg.text()}`);
    });

    // Capture network requests
    page.on('request', request => {
        console.log(`🌐 Request: ${request.method()} ${request.url()}`);
    });

    page.on('response', response => {
        console.log(`📡 Response: ${response.status()} ${response.url()}`);
    });

    console.log(`✅ Browser initialized and ready (${isHeadless ? 'headless' : 'headed'} mode)`);
    return page;
}

// HTTP Server for API commands
const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    try {
        let result = {};

        switch (pathname) {
            case '/status':
                if (MOCK_MODE) {
                    result = {
                        url: mockState.url,
                        title: mockState.title,
                        timestamp: new Date().toISOString(),
                        browserOpen: mockState.ready,
                        pageLoaded: mockState.ready,
                        mode: 'mock'
                    };
                } else {
                    try {
                        result = {
                            url: await page.url(),
                            title: await page.title(),
                            timestamp: new Date().toISOString(),
                            browserOpen: browser !== null,
                            pageLoaded: page !== null,
                            mode: 'playwright'
                        };
                    } catch (pageError) {
                        // Check if this is a session timeout error
                        if (isSessionTimeoutError(pageError)) {
                            console.log('🔄 Detected session timeout, attempting recovery...');
                            
                            // Clear the session cache
                            clearSessionCache();
                            
                            // Re-initialize browser
                            try {
                                if (browser) {
                                    await browser.close();
                                }
                                browser = null;
                                context = null;
                                page = null;
                                
                                // Re-initialize
                                await initializeBrowser();
                                
                                result = {
                                    url: await page.url(),
                                    title: await page.title(),
                                    timestamp: new Date().toISOString(),
                                    browserOpen: browser !== null,
                                    pageLoaded: page !== null,
                                    mode: 'playwright',
                                    recovered: true,
                                    recoveryReason: 'session_timeout'
                                };
                                console.log('✅ Session recovery successful');
                            } catch (recoveryError) {
                                console.error('❌ Session recovery failed:', recoveryError.message);
                                throw pageError; // Re-throw original error
                            }
                        } else {
                            throw pageError; // Re-throw if not a session timeout
                        }
                    }
                }
                break;

            case '/navigate':
                if (!query.url) {
                    throw new Error('URL parameter required');
                }
                console.log(`🧭 Navigating to: ${query.url}`);

                if (MOCK_MODE) {
                    // Simulate navigation delay
                    await new Promise(resolve => setTimeout(resolve, 500));
                    mockState.url = query.url;
                    mockState.title = `Mock Page: ${query.url}`;
                    result = { success: true, url: mockState.url, mode: 'mock' };
                } else {
                    await page.goto(query.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
                    result = {
                        success: true,
                        url: await page.url(),
                        title: await page.title(),
                        mode: 'playwright'
                    };
                    // Save session state after navigation
                    await saveCurrentSession();
                }
                break; case '/execute':
                if (!query.js) {
                    throw new Error('js parameter required');
                }
                console.log(`⚡ Executing JS: ${query.js}`);
                const executeResult = await page.evaluate(query.js);
                result = {
                    success: true,
                    result: executeResult
                };
                break;

            case '/dom':
                const selector = query.selector || 'body';
                console.log(`🔍 Getting DOM for selector: ${selector}`);
                const element = await page.$(selector);
                if (element) {
                    const innerHTML = await element.innerHTML();
                    result = {
                        success: true,
                        selector: selector,
                        html: innerHTML
                    };
                } else {
                    result = {
                        success: false,
                        error: `Element not found: ${selector}`
                    };
                }
                break;

            case '/screenshot':
                const name = query.name || `debug-${Date.now()}`;
                const screenshotPath = `/tmp/browser-screenshot-${name}.png`;
                console.log(`📸 Taking screenshot: ${screenshotPath}`);
                await page.screenshot({ path: screenshotPath, fullPage: true });
                result = {
                    success: true,
                    path: screenshotPath
                };
                break;

            case '/console':
                result = {
                    success: true,
                    logs: consoleLogs.slice(-20), // Last 20 entries
                    count: consoleLogs.length
                };
                break;

            case '/wait':
                if (!query.selector) {
                    throw new Error('selector parameter required');
                }
                console.log(`⏳ Waiting for selector: ${query.selector}`);
                const timeout = parseInt(query.timeout) || 10000;
                await page.waitForSelector(query.selector, { timeout });
                result = {
                    success: true,
                    selector: query.selector
                };
                break;

            case '/fill':
                if (!query.selector || !query.value) {
                    throw new Error('selector and value parameters required');
                }
                console.log(`✏️ Filling ${query.selector} with: ${query.value}`);
                await page.fill(query.selector, query.value);
                result = {
                    success: true,
                    selector: query.selector,
                    value: query.value
                };
                break;

            case '/click':
                if (!query.selector) {
                    throw new Error('selector parameter required');
                }
                console.log(`👆 Clicking: ${query.selector}`);
                await page.click(query.selector);
                result = {
                    success: true,
                    selector: query.selector
                };
                break;

            case '/health':
                result = { status: 'ok', timestamp: new Date().toISOString() };
                break;

            default:
                res.writeHead(404);
                res.end(JSON.stringify({ error: 'Endpoint not found' }));
                return;
        }

        res.writeHead(200);
        res.end(JSON.stringify(result, null, 2));

    } catch (error) {
        console.error(`❌ API Error [${pathname}]:`, error.message);
        res.writeHead(500);
        res.end(JSON.stringify({
            error: error.message,
            endpoint: pathname,
            timestamp: new Date().toISOString()
        }));
    }
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down...');

    // Save session state before closing
    await saveCurrentSession();

    if (browser) {
        console.log('🔒 Closing browser...');
        await browser.close();
    }

    server.close(() => {
        console.log('✅ Server closed');
        process.exit(0);
    });
});

// Start everything
async function main() {
    try {
        await initializeBrowser();

        const PORT = 3001;
        server.listen(PORT, () => {
            console.log(`🌐 Debug server running on http://localhost:${PORT}`);
            console.log('');
            console.log('Available endpoints:');
            console.log('  GET /status                    - Get current page status');
            console.log('  GET /navigate?url=<url>        - Navigate to URL');
            console.log('  GET /execute?js=<javascript>   - Execute JavaScript');
            console.log('  GET /dom?selector=<selector>   - Get DOM content');
            console.log('  GET /screenshot?name=<name>    - Take screenshot');
            console.log('  GET /console                   - Get console logs');
            console.log('  GET /wait?selector=<selector>  - Wait for element');
            console.log('  GET /fill?selector=<sel>&value=<val> - Fill input');
            console.log('  GET /click?selector=<selector> - Click element');
            console.log('');
            console.log('💡 Use browser-client.mjs for easier command-line interaction');
            console.log('📖 See README.md for usage examples');
            console.log('');
            console.log('🎯 Ready for browser automation development!');
            console.log('');
            console.log('🔄 Server is running in background. Press Ctrl+C to stop.');
        });

        // Keep the process alive and handle graceful shutdown
        process.stdin.resume();

        process.on('SIGINT', async () => {
            console.log('\n🛑 Shutting down gracefully...');
            // Save session state before closing
            await saveCurrentSession();
            if (browser) {
                console.log('🔒 Closing browser...');
                await browser.close();
            }
            process.exit(0);
        });

    } catch (error) {
        console.error('❌ Failed to start debug server:', error.message);
        process.exit(1);
    }
}

main();
