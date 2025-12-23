#!/usr/bin/env node

/*
 * Browser Debug Client - Command Line Interface for Debug Server
 *
 * This script provides a command-line interface to interact with the
 * browser debug server for iterative development and testing.
 *
 * Usage:
 *   node actions/browser-client.mjs <command> [args...]
 *
 * Examples:
 *   node actions/browser-client.mjs status
 *   node actions/browser-client.mjs navigate "https://example.com"
 *   node actions/browser-client.mjs execute "document.title"
 */

import http from 'http';
import fs from 'fs';

const SERVER_URL = 'http://localhost:3001';

// Make HTTP request to debug server
async function makeRequest(endpoint, params = {}) {
    return new Promise((resolve, reject) => {
        const queryString = new URLSearchParams(params).toString();
        const url = `${SERVER_URL}${endpoint}${queryString ? '?' + queryString : ''}`;

        const req = http.get(url, (res) => {
            let data = '';

            res.on('data', chunk => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    resolve(result);
                } catch (error) {
                    reject(new Error(`Failed to parse response: ${data}`));
                }
            });
        });

        req.on('error', error => {
            reject(new Error(`Request failed: ${error.message}`));
        });

        req.setTimeout(30000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });
    });
}

// Format and display results
function displayResult(result) {
    if (result.error) {
        console.error(`❌ Error: ${result.error}`);
        return;
    }

    if (result.success === false) {
        console.error(`❌ Failed: ${result.error || 'Unknown error'}`);
        return;
    }

    // Handle different response types
    switch (true) {
        case 'url' in result && 'title' in result:
            // Status response
            console.log(`📍 Current Page: ${result.title}`);
            console.log(`🌐 URL: ${result.url}`);
            console.log(`⏰ Time: ${result.timestamp}`);
            break;

        case 'html' in result:
            // DOM response
            console.log(`🔍 DOM Content for: ${result.selector}`);
            console.log('─'.repeat(80));

            // Truncate very long HTML
            let html = result.html;
            if (html.length > 2000) {
                html = html.substring(0, 2000) + '\n... (truncated, full content is ' + result.html.length + ' characters)';
            }
            console.log(html);
            console.log('─'.repeat(80));
            break;

        case 'result' in result:
            // Execute response - output raw JSON for machine consumption
            if (typeof result.result === 'object') {
                console.log(JSON.stringify(result.result, null, 2));
            } else {
                console.log(result.result);
            }
            break;

        case 'logs' in result:
            // Console logs response
            console.log(`📝 Console Logs (showing ${result.logs.length} of ${result.count} total):`);
            result.logs.forEach(log => {
                const time = new Date(log.timestamp).toLocaleTimeString();
                console.log(`[${time}] ${log.type.toUpperCase()}: ${log.text}`);
            });
            break;

        case 'path' in result:
            // Screenshot response
            console.log(`📸 Screenshot saved: ${result.path}`);
            break;

        default:
            // Generic success response
            console.log('✅ Success');
            if (Object.keys(result).length > 1) {
                console.log(JSON.stringify(result, null, 2));
            }
            break;
    }
}

// Show usage information
function showUsage() {
    console.log('Browser Debug Client - Command Line Interface');
    console.log('');
    console.log('Usage:');
    console.log('  node browser-client.mjs <command> [args...]');
    console.log('');
    console.log('Commands:');
    console.log('  status                           Get current page status');
    console.log('  navigate <url>                   Navigate to URL');
    console.log('  execute <javascript>             Execute JavaScript code');
    console.log('  dom [selector]                   Get DOM content (default: body)');
    console.log('  screenshot [name]                Take screenshot');
    console.log('  console                          Get recent console logs');
    console.log('  wait <selector> [timeout]        Wait for element (default: 10s)');
    console.log('  fill <selector> <value>          Fill input field');
    console.log('  click <selector>                 Click element');
    console.log('  help                             Show this help message');
    console.log('');
    console.log('Examples:');
    console.log('  node browser-client.mjs status');
    console.log('  node browser-client.mjs navigate "https://example.com"');
    console.log('  node browser-client.mjs execute "document.title"');
    console.log('  node browser-client.mjs dom "form"');
    console.log('  node browser-client.mjs fill "#searchBox" "search term"');
    console.log('  node browser-client.mjs click "#searchButton"');
    console.log('  node browser-client.mjs screenshot "after-action"');
    console.log('');
    console.log('💡 Make sure browser-server.mjs is running first!');
}

// Main command processing
async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0 || args[0] === 'help') {
        showUsage();
        return;
    }

    const command = args[0];

    try {
        let result;

        switch (command) {
            case 'status':
                result = await makeRequest('/status');
                break;

            case 'navigate':
                if (args.length < 2) {
                    console.error('❌ URL required');
                    console.log('Usage: node browser-client.mjs navigate <url>');
                    process.exit(1);
                }
                result = await makeRequest('/navigate', { url: args[1] });
                break;

            case 'execute':
                if (args.length < 2) {
                    console.error('❌ JavaScript code required');
                    console.log('Usage: node browser-client.mjs execute <javascript>');
                    process.exit(1);
                }
                result = await makeRequest('/execute', { js: args.slice(1).join(' ') });
                break;

            case 'execute-file':
                if (args.length < 2) {
                    console.error('❌ File path required');
                    console.log('Usage: node browser-client.mjs execute-file <file>');
                    process.exit(1);
                }
                const js = fs.readFileSync(args[1], 'utf8');
                result = await makeRequest('/execute', { js });
                break;

            case 'dom':
                const selector = args[1] || 'body';
                result = await makeRequest('/dom', { selector });
                break;

            case 'screenshot':
                const name = args[1] || `manual-${Date.now()}`;
                result = await makeRequest('/screenshot', { name });
                break;

            case 'console':
                result = await makeRequest('/console');
                break;

            case 'wait':
                if (args.length < 2) {
                    console.error('❌ Selector required');
                    console.log('Usage: node browser-client.mjs wait <selector> [timeout]');
                    process.exit(1);
                }
                const waitParams = { selector: args[1] };
                if (args[2]) {
                    waitParams.timeout = parseInt(args[2]) * 1000; // Convert to ms
                }
                result = await makeRequest('/wait', waitParams);
                break;

            case 'fill':
                if (args.length < 3) {
                    console.error('❌ Selector and value required');
                    console.log('Usage: node browser-client.mjs fill <selector> <value>');
                    process.exit(1);
                }
                result = await makeRequest('/fill', {
                    selector: args[1],
                    value: args.slice(2).join(' ')
                });
                break;

            case 'click':
                if (args.length < 2) {
                    console.error('❌ Selector required');
                    console.log('Usage: node browser-client.mjs click <selector>');
                    process.exit(1);
                }
                result = await makeRequest('/click', { selector: args[1] });
                break;

            default:
                console.error(`❌ Unknown command: ${command}`);
                console.log('Run "node browser-client.mjs help" for usage information');
                process.exit(1);
        }

        displayResult(result);

    } catch (error) {
        console.error(`❌ ${error.message}`);
        console.log('');
        console.log('💡 Troubleshooting:');
        console.log('  - Make sure browser-server.mjs is running');
        console.log('  - Check if server is accessible at http://localhost:3001');
        console.log('  - Verify the command syntax is correct');
        process.exit(1);
    }
}

main();
