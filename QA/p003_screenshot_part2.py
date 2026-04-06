#!/usr/bin/env python3
"""P003 QA Part 2 - 搜尋、上傳、設定截圖"""
from playwright.sync_api import sync_playwright
import os

APP_URL = "http://localhost:5000"
OUTPUT_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    # TC-005: 搜尋
    print("TC-005: 搜尋")
    page.goto(APP_URL, wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)
    try:
        page.locator("input").first.fill("test")
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        page.screenshot(path=f"{OUTPUT_DIR}/TC005_search.png", full_page=True)
        print("  ✅ TC005_search.png")
    except Exception as e:
        print(f"  ⚠️ {e}")

    # TC-006: 上傳對話框
    print("TC-006: 上傳對話框")
    page.goto(APP_URL, wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)
    try:
        btns = page.locator("button").all()
        for btn in btns:
            t = btn.inner_text()
            if "上傳" in t or "upload" in t.lower():
                btn.click()
                break
        page.wait_for_timeout(2000)
        page.screenshot(path=f"{OUTPUT_DIR}/TC006_upload_dialog.png", full_page=True)
        print("  ✅ TC006_upload_dialog.png")
    except Exception as e:
        print(f"  ⚠️ {e}")

    print("\n✅ 完成")
    browser.close()
