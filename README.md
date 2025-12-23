# Interactive Playwright Browser

Uses [Playwright](https://playwright.dev/) to browse any website.

Remotely orchestrate a browser, to navigate the web.
Meaning any task that can be accomplished via a browser.

## 🏗️ File Structure
```
actions/
├── README.md                 # This file - comprehensive guide and development log
├── browser-server.mjs        # Interactive browser debug server for development
├── browser-client.mjs        # Command-line interface for debugging
└── browser-server.sh         # Server management script
```

## 🚀 Quick Start

### Prerequisites
- Playwright must be installed: `npm install playwright`
  - or globally (and specifically) `npx playwright install chromium`

### Step 1: Start Interactive Debug Session
```bash
cd actions

# Option A: Use the management script (recommended)
./browser-server.sh start

# Option B: Start manually with custom options
node browser-server.mjs

# Option C: Test with mock mode (no real browser)
BROWSER_MOCK=true ./browser-server.sh start
```

### Step 2: Verify Connection
```bash
# Check server status
./browser-server.sh status

# Test client connection
node browser-client.mjs status

# Should show: URL: about:blank, ready for commands
```

### Step 3: Test Basic Browser Functions
```bash
# Test JavaScript execution
node browser-client.mjs execute "document.title = 'Browser Test'; 'success'"

# Test navigation to simple site
node browser-client.mjs navigate "https://httpbin.org/html"

# Check DOM inspection
node browser-client.mjs dom "h1"
```

### Step 4: Navigate to a Website and Explore
```bash
# Navigate to a website
node browser-client.mjs navigate "https://example.com"

# Take screenshot for reference
node browser-client.mjs screenshot "homepage"

# Check page content
node browser-client.mjs execute "document.body.innerText.includes('Example')"

# Examine page structure
node browser-client.mjs dom "h1"
```

### Step 5: Test Form Interaction (Example)
```bash
# Navigate to a page with a search form
node browser-client.mjs navigate "https://example.com/search"

# Examine search form
node browser-client.mjs dom "[type='search'], [name*='search'], [id*='search']"

# Test search input
node browser-client.mjs fill "[type='search']" "test query"

# Submit search
node browser-client.mjs click "[type='submit']"

# Wait and check results
node browser-client.mjs wait "[class*='result']"
node browser-client.mjs dom ".result"
```

## 🛠️ Server Management

### Using browser-server.sh (Recommended)
```bash
# Start server in background
./browser-server.sh start

# Check server status and logs
./browser-server.sh status

# Test server connection
./browser-server.sh test

# Stop server
./browser-server.sh stop

# Restart server
./browser-server.sh restart

# View live logs
./browser-server.sh logs
```

### Manual Server Control
```bash
# Start in headed mode (default)
node browser-server.mjs

# Start in headless mode
BROWSER_HEADLESS=true node browser-server.mjs

# Start in mock mode (testing only)
BROWSER_MOCK=true node browser-server.mjs
```

## 🛠️ Available Client Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `status` | Get current page info | `node browser-client.mjs status` |
| `navigate <url>` | Go to URL | `node browser-client.mjs navigate "https://example.com"` |
| `execute <js>` | Run JavaScript | `node browser-client.mjs execute "document.title"` |
| `dom [selector]` | Get HTML content | `node browser-client.mjs dom "#content"` |
| `screenshot [name]` | Take screenshot | `node browser-client.mjs screenshot debug1` |
| `console` | Get console logs | `node browser-client.mjs console` |
| `wait <selector>` | Wait for element | `node browser-client.mjs wait "[id*='results']"` |
| `fill <selector> <value>` | Fill input field | `node browser-client.mjs fill "#searchBox" "test"` |
| `click <selector>` | Click element | `node browser-client.mjs click "#submitButton"` |
| `help` | Show usage info | `node browser-client.mjs help` |

## 🔍 Browser Exploration Process

### Page Analysis
```bash
# Find form elements
node browser-client.mjs execute "Array.from(document.querySelectorAll('form')).map(f => ({action: f.action, method: f.method}))"
```

### Element Discovery
```bash
# Find interactive elements
node browser-client.mjs execute "Array.from(document.querySelectorAll('input, button, a')).filter(el => el.id || el.name).map(el => ({tag: el.tagName, id: el.id, name: el.name, type: el.type}))"
```

### Dynamic Content Monitoring
```bash
# Check for AJAX requests
node browser-client.mjs execute "window.performance.getEntriesByType('xmlhttprequest').length"
```

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check port availability
lsof -i :3001

# Kill any processes using port 3001
./browser-server.sh stop
# or manually: lsof -ti:3001 | xargs kill -9

# Check server logs
./browser-server.sh status
```

### Client Connection Issues
```bash
# Test server directly
curl -s http://localhost:3001/status

# Check if server is running
./browser-server.sh status

# Restart server if needed
./browser-server.sh restart
```

### Navigation Timeouts
- External sites may be slow; try local testing first
- Use mock mode for testing: `BROWSER_MOCK=true ./browser-server.sh start`
- Check if headed browser window is responding

### Form Interaction Issues
- Take screenshot to see current state: `node browser-client.mjs screenshot error-state`
- Check console for JavaScript errors: `node browser-client.mjs console`
- Verify selectors are correct: `node browser-client.mjs dom "form"`

## 🔧 Configuration Options

### Environment Variables
- `BROWSER_MOCK=true` - Enable mock mode (no real browser)
- `BROWSER_HEADLESS=true` - Run browser in headless mode
- `BROWSER_HEADED=true` - Force headed mode (deprecated, headed is now default)

### Command Line Options
- `--mock` - Enable mock mode
- `--headless` - Run in headless mode
- `--headed` - Run in headed mode (deprecated)

## 📁 Output Files

- **Screenshots**: Saved to current directory as `browser-screenshot-*.png`
- **Server Logs**: `browser-server.log` (when using browser-server.sh)
- **PID File**: `browser-server.pid` (server process tracking)
- **Debug Output**: All client commands show formatted results in terminal

## 🔄 Development Workflow

### Phase 1: Setup and Verification
1. **Start Server**: `./browser-server.sh start`
2. **Test Connection**: `node browser-client.mjs status`
3. **Test Browser**: Navigate to simple site and verify functionality

### Phase 2: Website Exploration
1. **Navigate to Site**: Use client to reach target website
2. **Verify Access**: Check page loads correctly
3. **Explore Structure**: Use DOM inspection to understand page layout
4. **Document Progress**: Take screenshots and note selectors

### Phase 3: Interaction Implementation
1. **Find Elements**: Locate input fields and buttons
2. **Test Interactions**: Fill and submit forms manually via client
3. **Monitor AJAX**: Watch for dynamic content loading
4. **Extract Results**: Parse response data and test extraction

## 🎯 Current Status

### ✅ Completed
- ✅ Interactive debug server with HTTP API
- ✅ Command-line client interface  
- ✅ Server management script
- ✅ Mock mode for testing without browser
- ✅ Real browser functionality verified
- ✅ Navigation and DOM manipulation working
- ✅ JavaScript execution capability confirmed
- ✅ End-to-end browser automation operational

### 📋 TODO
- 📋 Add support for different authentication methods
- 📋 Implement cookie/session management
- 📋 Add proxy configuration options
- 📋 Enhance error handling and recovery

## 🎯 Success Criteria

The development is complete when:
- ✅ Browser can navigate to any website
- ✅ Forms can be identified and filled
- ✅ User interactions can be simulated
- ✅ Content can be extracted from pages
- ✅ Screenshots and debugging work reliably
- ✅ Automated browser tasks can be scripted

## 💡 Tips for Future Development

### General Best Practices
- Always start with `./browser-server.sh status` to understand current state
- Use `node browser-client.mjs status` to check browser state before each step
- Take screenshots liberally: `node browser-client.mjs screenshot step-N`
- Check console logs after each interaction: `node browser-client.mjs console`

### Website-Specific Tips
- Different sites may require different authentication methods
- Forms may use various frameworks with dynamic content
- Dynamic content loading requires waiting for elements
- Test small JavaScript snippets before implementing automation

### Debugging Techniques
- Use `dom` with specific selectors to examine form structure
- Test small JavaScript snippets with `execute` before implementing
- Monitor browser window visually for loading states and errors
- Use `wait` command for elements that load dynamically

### Performance Considerations
- Navigation to external sites may timeout - use mock mode for testing
- Headed mode is better for debugging, headless for production
- Keep debug server running throughout development session
- Use `./browser-server.sh restart` if browser becomes unresponsive

## 🚨 Important Notes

### Security
- **Never commit credentials** - use environment variables only
- Browser runs with user's authentication context
- Avoid writing/reading password to stdin or from stdout

### Session Management
- Authentication is maintained across navigation within session
- Browser state persists until server restart
- Use Ctrl+C or `./browser-server.sh stop` to cleanly shutdown

### File Dependencies
- Playwright must be installed: `npm install playwright`
- All scripts are ES modules (.mjs) - ensure Node.js v14+ support

## 🔗 Quick Reference

### Essential Commands
```bash
# Complete startup sequence
cd actions
./browser-server.sh start
node browser-client.mjs status

# Development cycle
node browser-client.mjs navigate "https://example.com"
node browser-client.mjs screenshot step1
node browser-client.mjs dom "form"
node browser-client.mjs execute "/* test code */"

# Cleanup
./browser-server.sh stop
```

### File Locations
- Server script: `actions/browser-server.mjs`
- Client script: `actions/browser-client.mjs`  
- Management script: `actions/browser-server.sh`
- Documentation: `README.md` (this file)
