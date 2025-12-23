---
name: browser
description: remotely orchestrate a (chromium) browser to utilize web apps
---

# Browser

Uses [Playwright](https://playwright.dev/) to browse any website.
Remotely orchestrate a browser, to navigate the web.
Meaning any task that can be accomplished via a browser.

## Instructions

- read `README.md` to understand this project

## QUICK REFERENCE

These are CLI commands you may use.

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

## Examples

Sample user prompt:

> let's test this project:
> - start browser service
> - use client scripts to 
>   - navigate to google.com
>   - check for presence of search input box
>   - type `hamster dance` into search box
>   - click search button
>   - read first 3 search results
>   - summarize them in your response to me

Sample agent output (ie. `Gemini 3 Flash`):

```
GitHub Copilot: Created 8 todos

Read [](file:///workspace/cli/browser/README.md#1-1), lines 1 to 100

Starting: *Start browser service* (2/8)

Ran terminal command: cd /workspace/cli/browser/actions && ./browser-server.sh start

Ran terminal command: node browser-server.mjs

Ran terminal command: npx playwright install chromium

Ran terminal command: ./browser-server.sh start

Ran terminal command: ./browser-server.sh status

Starting: *Navigate to Google* (3/8)

Ran terminal command: node browser-client.mjs navigate "https://www.google.com"

Starting: *Check search box* (4/8)

Ran terminal command: node browser-client.mjs dom "[name='q']"

Ran terminal command: node browser-client.mjs execute "document.querySelector('[name=\'q\']') ? 'Found' : 'Not Found'"

Starting: *Type search query* (5/8)

Ran terminal command: node browser-client.mjs fill "[name='q']" "hamster dance"

Starting: *Click search button* (6/8)

Ran terminal command: node browser-client.mjs execute "document.querySelector('[name=\'btnK\']').click()"

Ran terminal command: node browser-client.mjs wait "#search" 5000

Starting: *Read search results* (7/8)

Ran terminal command: node browser-client.mjs execute "Array.from(document.querySelectorAll('#search h3')).slice(0, 3).map(h3 => ({title: h3.innerText, link: h3.closest('a')?.href}))"

Starting: *Summarize results* (8/8)

Completed: *Summarize results* (8/8)

The browser service was successfully started, and I performed the requested search for "hamster dance" on Google. Here are the first three search results:

1.  **Hampton the Hamster "The Hamsterdance Song"**
    *   **Link:** [https://www.youtube.com/watch?v=p3G5IXn0K7A](https://www.youtube.com/watch?v=p3G5IXn0K7A)
    *   **Summary:** The official music video for the viral "Hamsterdance Song" featuring Hampton the Hamster.

2.  **The Original Hampster Dance - YTMND**
    *   **Link:** [https://originalhampster.ytmnd.com/](https://originalhampster.ytmnd.com/)
    *   **Summary:** A classic YTMND page hosting the original animated GIF loop and music that started the internet phenomenon.

3.  **Hampster Dance**
    *   **Link:** [https://en.wikipedia.org/wiki/Hampster_Dance](https://en.wikipedia.org/wiki/Hampster_Dance)
    *   **Summary:** The Wikipedia entry detailing the history, creation, and cultural impact of the Hampster Dance, one of the earliest internet memes.
```