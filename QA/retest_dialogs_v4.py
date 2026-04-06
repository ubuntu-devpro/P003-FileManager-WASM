#!/usr/bin/env python3
"""P003 QA - 對話框截圖，使用精確 selector"""
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"
BASE_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/test_cases"

def login(page):
    page.goto(f"{APP_URL}/login", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    page.wait_for_timeout(6000)
    page.wait_for_selector("tbody tr", timeout=10000)
    page.wait_for_timeout(2000)

def wait_dialog(page):
    page.wait_for_selector("[role='dialog'], .rz-dialog", timeout=10000)

def ss(page, path):
    page.wait_for_timeout(2000)
    page.screenshot(path=path, full_page=True)

def new_page_test(name, dest, screenshot, click_selector, wait_dialog_flag=True):
    print(f"\n{name}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()

        login(page)

        try:
            page.click(click_selector, timeout=5000)
            if wait_dialog_flag:
                wait_dialog(page)
                page.wait_for_timeout(2000)
            ss(page, f"{dest}/{screenshot}")
            print(f"  ✅ {name} 成功")
        except Exception as e:
            print(f"  ⚠️ {name}: {e}")
            ss(page, f"{dest}/{screenshot}")

        ctx.close()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()

    login(page)

    # 先觀察所有按鈕
    print("\n觀察頁面上的按鈕:")
    buttons = page.locator("button").all()
    for i, btn in enumerate(buttons):
        try:
            txt = btn.inner_text()
            cls = btn.get_attribute("class") or ""
            print(f"  [{i}] class='{cls}' text='{txt}'")
        except:
            pass

    # FM-002: 新增資料夾 - 找 toolbar 中的新增按鈕
    print("\n=== FM-002: 新增資料夾 ===")
    # toolbar 通常在頂部，找第一個按鈕
    toolbar_btns = page.locator(".fm-toolbar button").all()
    print(f"  toolbar 按鈕數量: {len(toolbar_btns)}")
    for i, btn in enumerate(toolbar_btns):
        try:
            txt = btn.inner_text()
            print(f"  [{i}] '{txt}'")
        except:
            pass

    browser.close()
