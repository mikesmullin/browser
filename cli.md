## QUICK REFERENCE

| Task | Command | Purpose |
|------|---------|---------|
| Start Browser Server | [](actions/browser-server.sh) start | Start background browser server with Playwright session |
| Stop Browser Server | [](actions/browser-server.sh) stop | Stop background server |
| Server Status | [](actions/browser-server.sh) status | Check server status and latest logs summary |
| Restart Browser Server | [](actions/browser-server.sh) restart | Restart background server |
| View Live Logs | [](actions/browser-server.sh) logs | Tail live server logs |
| Get Page Status | [](actions/browser-client.mjs) status | Get current page URL and title |
| Navigate to URL | [](actions/browser-client.mjs) navigate URL | Navigate browser to specified URL |
| Execute JavaScript | [](actions/browser-client.mjs) execute JAVASCRIPT | Execute JavaScript code in browser context |
| Get DOM Content | [](actions/browser-client.mjs) dom [SELECTOR] | Get HTML content of element (default: body) |
| Take Screenshot | [](actions/browser-client.mjs) screenshot [NAME] | Capture screenshot of current page |
| Get Console Logs | [](actions/browser-client.mjs) console | Retrieve recent browser console logs |
| Wait for Element | [](actions/browser-client.mjs) wait SELECTOR [TIMEOUT] | Wait for element to appear (default timeout: 10s) |
| Fill Input Field | [](actions/browser-client.mjs) fill SELECTOR VALUE | Fill form input field with value |
| Click Element | [](actions/browser-client.mjs) click SELECTOR | Click on specified element |