---
name: browser
description: remotely orchestrate a (chromium) browser to utilize web apps
---

# Browser

Uses [browser-use](https://github.com/browser-use/browser-use) (via Chrome DevTools Protocol) to browse any website.
Remotely orchestrate a browser, to navigate the web.
Meaning any task that can be accomplished via a browser.

## Instructions

- read `README.md` to understand this project

## QUICK REFERENCE

These are CLI commands you may use.

| Task | Command | Purpose |
|------|---------|---------|
| Start Browser Server | [](src/browser-server.sh) start | Start background browser server |
| Stop Browser Server | [](src/browser-server.sh) stop | Stop background server |
| Server Status | [](src/browser-server.sh) status | Check server status and latest logs summary |
| Restart Browser Server | [](src/browser-server.sh) restart | Restart background server |
| View Live Logs | [](src/browser-server.sh) logs | Tail live server logs |
| Get Page Status | `python src/browser_client.py status` | Get current page URL and title |
| Navigate to URL | `python src/browser_client.py navigate URL` | Navigate browser to specified URL |
| Execute JavaScript | `python src/browser_client.py execute JAVASCRIPT` | Execute JavaScript code (arrow function) |
| Get DOM Content | `python src/browser_client.py dom [SELECTOR]` | Get HTML content of element (default: body) |
| Fill Input Field | `python src/browser_client.py fill SELECTOR VALUE` | Fill form input field with value |
| Click Element | `python src/browser_client.py click SELECTOR` | Click on specified element |

## Examples

Sample user prompt:

> let's test this project:
> - start browser service
> - use client scripts to 
>   - navigate to google.com
>   - type `hamster dance` into search box
>   - click search button
>   - read first 3 search results
>   - summarize them in your response to me
>   - stop the server

Sample agent output (ie. `Gemini 3 Flash`):

```
GitHub Copilot: Created 6 todos

Starting: *Start browser service* (1/6)

Ran terminal command: source .venv/bin/activate && cd src && ./browser-server.sh start

Stdout:
Starting browser server...
✅ Server started (PID 12345)

Starting: *Navigate to Google* (2/6)

Ran terminal command: python browser_client.py navigate "https://www.google.com"

Stdout:
✅ Navigated to https://www.google.com

Starting: *Type search query* (3/6)

Ran terminal command: python browser_client.py fill "[name='q']" "hamster dance"

Stdout:
✅ Filled [name='q']

Starting: *Click search button* (4/6)

Ran terminal command: python browser_client.py click "[name='btnK']"

Stdout:
✅ Clicked [name='btnK']

Starting: *Read search results* (5/6)

Ran terminal command: python browser_client.py execute "() => Array.from(document.querySelectorAll('#search h3')).slice(0, 3).map(h3 => ({title: h3.innerText, link: h3.closest('a')?.href}))"

Stdout:
Result: [{"title": "Hampton the Hamster \"The Hamsterdance Song\"", "link": "https://www.youtube.com/watch?v=1qN72LEQnaU"}, ...]

Starting: *Stop server* (6/6)

Ran terminal command: ./browser-server.sh stop

Stdout:
✅ Server stopped (PID 12345)

Completed: *Summarize results*

The browser service was successfully started, and I performed the requested search for "hamster dance" on Google. Here are the first three search results:

1.  **Hampton the Hamster "The Hamsterdance Song"**
    - [https://www.youtube.com/watch?v=1qN72LEQnaU](https://www.youtube.com/watch?v=1qN72LEQnaU)
2.  **Hampton the Hamster - The Hamsterdance Song (Official Video ...**
    - [https://www.youtube.com/watch?v=6WpMlwVwydo](https://www.youtube.com/watch?v=6WpMlwVwydo)
3.  **Hamster Dance - Wikipedia**
    - [https://en.wikipedia.org/wiki/Hamster_Dance](https://en.wikipedia.org/wiki/Hamster_Dance)
```
