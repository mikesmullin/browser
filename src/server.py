
import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from browser_use import Browser, BrowserProfile
from browser_use.browser.session import BrowserSession
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
browser: BrowserSession = None
browser_context = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global browser, browser_context
    logger.info("🚀 Starting Browser Use server...")
    
    # Determine user data directory
    from pathlib import Path
    user_data_dir = Path.home() / ".browser_agent"
    
    logger.info(f"📂 Using user data directory: {user_data_dir}")
    
    # Initialize browser with default configuration
    # Note: browser-use uses CDP directly now, no Playwright dependency needed
    browser = Browser(
        headless=False,  # Run in headed mode for visibility
        user_data_dir=user_data_dir,
    )
    
    # Start the browser
    await browser.start()
    
    yield
    
    # Shutdown
    logger.info("🛑 Stopping Browser Use server...")
    if browser:
        await browser.stop()

app = FastAPI(lifespan=lifespan)

class NavigateRequest(BaseModel):
    url: str

class SelectorRequest(BaseModel):
    selector: str

class FillRequest(BaseModel):
    selector: str
    value: str

class ExecuteRequest(BaseModel):
    script: str

class ScreenshotRequest(BaseModel):
    full_page: bool = False

@app.get("/")
async def root():
    return {"status": "running", "service": "browser-use-server"}

@app.get("/status")
async def status():
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        page = await browser.get_current_page()
        # Page object in browser-use might have async methods for url/title or different attributes
        # Let's try to inspect it or use async methods if they exist
        # Based on error 'Page' object has no attribute 'url', it might be a method or different name
        
        # Let's try to get url via CDP or check if it's a method
        # If it's a CDP Page wrapper, it might have get_url() or similar
        
        # Let's try to use the browser session methods if available
        # browser.get_current_page_url() seems to exist in dir(Browser) we saw earlier!
        
        url = await browser.get_current_page_url()
        title = await browser.get_current_page_title()
        
        return {
            "url": url,
            "title": title,
            "ready": True
        }
    except Exception as e:
        return {"ready": False, "error": str(e)}

@app.post("/navigate")
async def navigate(request: NavigateRequest):
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        # browser-use Browser class has navigate_to method
        await browser.navigate_to(request.url)
        return {"success": True, "url": request.url}
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/click")
async def click(request: SelectorRequest):
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        # Re-implementing click using execute for now
        # browser-use requires arrow function format: (...args) => { ... }
        script = f"""
        () => {{
            const el = document.querySelector("{request.selector}");
            if (el) {{
                el.click();
                return true;
            }}
            return false;
        }}
        """
        return await execute(ExecuteRequest(script=script))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute(request: ExecuteRequest):
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        page = await browser.get_current_page()
        # browser-use evaluate expects arrow function string if it's not a simple expression?
        # The error message said: "JavaScript code must start with (...args) => format"
        
        script = request.script.strip()
        if not script.startswith("(") and "=>" not in script:
             # Wrap simple expressions or statements in arrow function if needed
             # But if the user provides a full script, we might need to adapt it.
             # For now, let's assume the user (or our internal calls) provides the correct format
             # OR we wrap it if it doesn't look like an arrow function.
             pass

        result = await page.evaluate(script)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/screenshot")
async def screenshot(request: ScreenshotRequest):
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        page = await browser.get_current_page()
        logger.info(f"Page type: {type(page)}")
        logger.info(f"Page dir: {dir(page)}")
        
        # Ensure screenshots directory exists
        from pathlib import Path
        import time
        # Save to workspace local dir
        screenshots_dir = Path(__file__).parent.parent / ".browser_data" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"screenshot_{int(time.time())}.png"
        filepath = screenshots_dir / filename
        
        # Try calling screenshot without path first to see what it returns
        result = await page.screenshot()
        logger.info(f"Screenshot result type: {type(result)}")
        
        if isinstance(result, bytes):
            with open(filepath, "wb") as f:
                f.write(result)
        elif isinstance(result, str):
            # Maybe it's base64?
            import base64
            try:
                data = base64.b64decode(result)
                with open(filepath, "wb") as f:
                    f.write(data)
            except:
                # Maybe it's a path?
                logger.info(f"Screenshot result string: {result}")
        
        return {"success": True, "path": str(filepath)}
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/click")
async def click_endpoint(request: SelectorRequest):
    return await click(request)

@app.post("/fill")
async def fill_endpoint(request: FillRequest):
    # Re-implementing fill using execute for now
    script = f"""
    () => {{
        const el = document.querySelector("{request.selector}");
        if (el) {{
            el.value = "{request.value}";
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}
        return false;
    }}
    """
    return await execute(ExecuteRequest(script=script))

@app.post("/dom")
async def dom_endpoint(request: SelectorRequest):
    selector = request.selector or "body"
    script = f"""
    () => {{
        const el = document.querySelector("{selector}");
        return el ? el.outerHTML : "";
    }}
    """
    return await execute(ExecuteRequest(script=script))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
