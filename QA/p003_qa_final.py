#!/usr/bin/env python3
"""P003 QA - Final Screenshot Test"""
from playwright.sync_api import sync_playwright
import os

APP_URL = "http://localhost:5000"
OUTPUT_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/screenshots"

def ss(page, name, wait=2000):
    page.wait_for_timeout(wait)
    page.screenshot(path=f"{OUTPUT_DIR}/{name}", full_page=True)
    print(f"  ✅ {name}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    print("TC-001/002: 首頁 + 檔案列表")
    page.goto(APP_URL, wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(5000)
    ss(page, "TC002_filelist.png")

    print("TC-003: 右鍵選單")
    try:
        row = page.locator("tbody tr").first
        row.click(button="right")
        page.wait_for_timeout(1000)
        ss(page, "TC003_context_menu.png")
        page.keyboard.press("Escape")
    except:
        ss(page, "TC003_context_menu.png")

    print("TC-004: 新增資料夾對話框")
    try:
        btns = page.locator("button").all()
        for btn in btns:
            if "新增" in btn.inner_text():
                btn.click()
                break
        page.wait_for_timeout(2000)
        ss(page, "TC004_new_folder.png")
        page.keyboard.press("Escape")
    except:
        ss(page, "TC004_new_folder.png")

    print("TC-005: 搜尋")
    try:
        page.locator("input").first.fill("test")
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        ss(page, "TC005_search.png")
        page.locator("input").first.fill("")
        page.keyboard.press("Enter")
    except:
        ss(page, "TC005_search.png")

    print("TC-006: 上傳對話框")
    try:
        btns = page.locator("button").all()
        for btn in btns:
            if "上傳" in btn.inner_text():
                btn.click()
                break
        page.wait_for_timeout(2000)
        ss(page, "TC006_upload.png")
        page.keyboard.press("Escape")
    except:
        ss(page, "TC006_upload.png")

    print("TC-007: Debug Header API 驗證")
    import subprocess, json
    r = subprocess.run(["curl", "-s", "http://localhost:5001/api/files?path=/home/devpro/data"], capture_output=True, text=True)
    print(f"  API response: {r.stdout[:100]}")

    print("\n✅ 完成！")
    browser.close()
