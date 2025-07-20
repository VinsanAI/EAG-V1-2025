# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from win32api import GetSystemMetrics
import asyncio
import functools

# instantiate an MCP server client
mcp = FastMCP("Simple paint automation")

def async_time_tracker_decorator(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        total_time = time.time() - start_time
        print(f"Total time taken is: {total_time}\n")
        return result
    return wrapper

@mcp.tool()
@async_time_tracker_decorator
async def open_paint() -> None:
    """Open Microsoft Paint maximized on secondary monitor"""
    global paint_app
    try:
        paint_app = Application().start('mspaint.exe')
        time.sleep(0.2)

        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')

        # Get primary monitor width
        primary_width = GetSystemMetrics(0)

        # First move to secondary monitor without specifying size
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            primary_width + 1, 0,  # Position it on secondary monitor
            # 0, 0,
            0, 0,  # Let Windows handle the size
            win32con.SWP_NOSIZE  # Don't change the size
        )

        # Now maximize the window
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(0.2)
        print("Successfully opened the paint application")
    except Exception as e:
        print("Failed with error")

@mcp.tool()
@async_time_tracker_decorator
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> None:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""

    global paint_app
    try:
        if not paint_app:
            print("Failed with error")
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width to adjust coordinates
        primary_width = GetSystemMetrics(0)
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.2)
        
        # Click on the Rectangle tool using the correct coordinates for secondary screen
        paint_window.click_input(coords=(543, 93))
        time.sleep(0.2)
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Draw rectangle - coordinates should already be relative to the Paint window
        # No need to add primary_width since we're clicking within the Paint window
        canvas.press_mouse_input(coords=(x1+2560, y1))
        canvas.move_mouse_input(coords=(x2+2560, y2))
        canvas.release_mouse_input(coords=(x2+2560, y2))
        print("Successfully drawn rectangle in paint")
    except Exception as e:
        print("Failed with error")

@mcp.tool()
@async_time_tracker_decorator
async def add_text_in_paint(text: str) -> None:
    """Add text in Paint"""
    global paint_app
    try:
        if not paint_app:
            print("Failed with error")
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)
        
        # # Click on the Rectangle tool
        # paint_window.click_input(coords=(528, 92))
        # time.sleep(0.5)
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Select text tool using keyboard shortcuts
        paint_window.type_keys('t')
        time.sleep(0.5)
        paint_window.type_keys('x')
        time.sleep(0.5)

        # Selecting bigger font size
        paint_window.click_input(coords=(848, 206))
        time.sleep(0.2)
        paint_window.click_input(coords=(841, 543))
        time.sleep(0.2)
        
        # Click where to start typing
        canvas.click_input(coords=(1189, 540))
        time.sleep(0.5)
        
        # Type the text passed from client
        paint_window.type_keys(text)
        time.sleep(0.5)
        
        # Click to exit text mode
        canvas.click_input(coords=(1050, 800))
        
        print("Successfully added text in paint")
    except Exception as e:
        print("Failed with error")

@async_time_tracker_decorator
async def main():
    print("Initiating Main Function\n"+50*"-"+"\n")
    await asyncio.gather(open_paint(),
    draw_rectangle(x1=380, 
                y1=380, 
                x2=1140, 
                y2=700),
    add_text_in_paint("Add this text"))
    print(50*"-"+"\nSuccessfully completed Main Function")

asyncio.run(main())