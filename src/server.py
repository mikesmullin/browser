
import os
import asyncio
import logging
import time
import io
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from browser_use import Browser, BrowserProfile
from browser_use.browser.session import BrowserSession
from contextlib import asynccontextmanager
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
browser: BrowserSession = None
browser_context = None
yolo_model = None
sam_model = None

# Ensure models directory exists
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Ensure screenshots directory exists in workspace root
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def get_yolo():
    global yolo_model
    if yolo_model is None:
        from ultralytics import YOLO
        model_path = MODELS_DIR / "yolov8n.pt"
        logger.info(f"📥 Loading YOLO model ({model_path})...")
        yolo_model = YOLO(str(model_path))
    return yolo_model

def get_sam():
    global sam_model
    if sam_model is None:
        from ultralytics import SAM
        model_path = MODELS_DIR / "sam_b.pt"
        logger.info(f"📥 Loading SAM model ({model_path})...")
        sam_model = SAM(str(model_path))
    return sam_model

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

class ClickAtRequest(BaseModel):
    x: int
    y: int

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

@app.post("/click_at")
async def click_at(request: ClickAtRequest):
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        page = await browser.get_current_page()
        # browser-use Page.mouse is a coroutine that returns a Mouse object
        mouse = await page.mouse
        await mouse.click(request.x, request.y)
        return {"success": True, "x": request.x, "y": request.y}
    except Exception as e:
        logger.error(f"Click at ({request.x}, {request.y}) failed: {e}")
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
        
        filename = f"screenshot_{int(time.time())}.png"
        filepath = SCREENSHOTS_DIR / filename
        
        # Try calling screenshot without path first to see what it returns
        result = await page.screenshot()
        
        if isinstance(result, bytes):
            with open(filepath, "wb") as f:
                f.write(result)
        
        return {"success": True, "path": str(filepath)}
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize")
async def visualize():
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        page = await browser.get_current_page()
        
        # 1. Get interactive elements and their rects via JS
        script = """
        () => {
            const interactives = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"], [onclick]'));
            return interactives.map(el => {
                const rect = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    text: (el.innerText || "").slice(0, 20),
                    x: rect.left,
                    y: rect.top,
                    w: rect.width,
                    h: rect.height,
                    visible: rect.width > 0 && rect.height > 0 && el.offsetParent !== null
                };
            }).filter(item => item.visible);
        }
        """
        response = await page.evaluate(script)
        
        elements = response
        if isinstance(response, str):
            import json
            try:
                elements = json.loads(response)
            except Exception as je:
                logger.error(f"Failed to parse evaluate response as JSON: {je}")
                elements = []
        elif isinstance(response, dict) and 'result' in response:
            elements = response['result']
        
        if not isinstance(elements, list):
            logger.error(f"Elements is not a list: {elements}")
            elements = []
        
        screenshot_bytes = await page.screenshot()
        
        if isinstance(screenshot_bytes, str):
            import base64
            screenshot_bytes = base64.b64decode(screenshot_bytes)
        
        # 3. Draw rects using PIL
        from PIL import Image, ImageDraw, ImageFont
        import io
        from pathlib import Path
        import time
        
        img = Image.open(io.BytesIO(screenshot_bytes))
        draw = ImageDraw.Draw(img)
        
        for i, el in enumerate(elements):
            # Draw rectangle
            shape = [el['x'], el['y'], el['x'] + el['w'], el['y'] + el['h']]
            draw.rectangle(shape, outline="red", width=2)
            # Draw label
            draw.text((el['x'], el['y'] - 10), f"{i}", fill="red")
            
        # Save visualized image
        timestamp = int(time.time())
        filename = f"visualized_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        img.save(filepath)
        
        # Create compact CSV representation: x,y,id,text
        csv_data = []
        for i, el in enumerate(elements):
            # Use center coordinates for clicking
            cx = int(el['x'] + el['w'] / 2)
            cy = int(el['y'] + el['h'] / 2)
            # Sanitize text: remove commas and newlines
            text = el.get('text', "").replace(",", " ").replace("\n", " ").strip()
            csv_data.append(f"{cx},{cy},{i},{text}")
        
        csv_filename = f"visualized_{timestamp}.csv"
        csv_filepath = SCREENSHOTS_DIR / csv_filename
        with open(csv_filepath, "w") as f:
            f.write("\n".join(csv_data))
        
        return {
            "success": True, 
            "path": str(filepath), 
            "csv_path": str(csv_filepath),
            "elements_count": len(elements),
            "csv": "\n".join(csv_data)
        }
    except Exception as e:
        logger.error(f"Visualization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect")
async def detect():
    """Detect objects in the current page using YOLO."""
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        page = await browser.get_current_page()
        screenshot_bytes = await page.screenshot()
        
        if isinstance(screenshot_bytes, str):
            import base64
            screenshot_bytes = base64.b64decode(screenshot_bytes)
            
        img = Image.open(io.BytesIO(screenshot_bytes))
        
        model = get_yolo()
        results = model(img)
        
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                label = model.names[cls]
                detections.append({
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "conf": conf, "label": label
                })
        
        # Draw detections
        draw = ImageDraw.Draw(img)
        csv_data = []
        for i, d in enumerate(detections):
            draw.rectangle([d['x1'], d['y1'], d['x2'], d['y2']], outline="yellow", width=3)
            draw.text((d['x1'], d['y1'] - 10), f"{d['label']} {d['conf']:.2f}", fill="yellow")
            
            cx = int((d['x1'] + d['x2']) / 2)
            cy = int((d['y1'] + d['y2']) / 2)
            csv_data.append(f"{cx},{cy},{i},{d['label']}")

        # Save result
        timestamp = int(time.time())
        filename = f"detected_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        img.save(filepath)
        
        return {
            "success": True,
            "detections": detections,
            "image_path": str(filepath),
            "csv": "\n".join(csv_data)
        }
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/segment")
async def segment():
    """Segment objects in the current page using SAM."""
    if not browser:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    try:
        page = await browser.get_current_page()
        screenshot_bytes = await page.screenshot()
        
        if isinstance(screenshot_bytes, str):
            import base64
            screenshot_bytes = base64.b64decode(screenshot_bytes)
            
        img = Image.open(io.BytesIO(screenshot_bytes))
        
        model = get_sam()
        results = model(img)
        
        # SAM results are different, usually masks
        # For simplicity, we'll just save the result image if possible
        # or return the count of segments
        
        timestamp = int(time.time())
        filename = f"segmented_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        
        # Save the first result's plotted image
        # plot() returns a numpy array (BGR)
        # We enable boxes=True because labels often depend on boxes being drawn.
        # line_width=1 keeps the boxes from being too thick.
        plotted_img = results[0].plot(labels=True, boxes=True, conf=True, line_width=1)
        # Convert BGR to RGB for PIL
        import cv2
        plotted_img_rgb = cv2.cvtColor(plotted_img, cv2.COLOR_BGR2RGB)
        Image.fromarray(plotted_img_rgb).save(str(filepath))
        
        # Create CSV mapping for segments: cx,cy,id,label
        csv_data = []
        if results[0].boxes:
            for i, box in enumerate(results[0].boxes):
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                csv_data.append(f"{cx},{cy},{i},segment")
        
        return {
            "success": True,
            "image_path": str(filepath),
            "segments_count": len(results[0].masks) if results[0].masks else 0,
            "csv": "\n".join(csv_data)
        }
    except Exception as e:
        logger.error(f"Segmentation failed: {e}")
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
