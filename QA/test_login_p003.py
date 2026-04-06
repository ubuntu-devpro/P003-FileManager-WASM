#!/usr/bin/env python3
"""P003 - Test Login UI and domain permissions"""
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"
OUTPUT_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    # TC-Login-001: Login page
    print("TC-Login-001: Login page")
    page.goto(f"{APP_URL}/login", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)
    page.screenshot(path=f"{OUTPUT_DIR}/TC_Login001_login_page.png", full_page=True)
    print("  ✅ Login page screenshot")

    # TC-Login-002: Login as admin
    print("TC-Login-002: Admin login")
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    page.wait_for_timeout(5000)
    page.screenshot(path=f"{OUTPUT_DIR}/TC_Login002_admin_dashboard.png", full_page=True)
    print(f"  URL: {page.url}")
    print("  ✅ Admin dashboard screenshot")

    # TC-Login-003: Logout
    print("TC-Login-003: Logout")
    try:
        page.click(".logout-btn")
        page.wait_for_timeout(2000)
        page.screenshot(path=f"{OUTPUT_DIR}/TC_Login003_after_logout.png", full_page=True)
        print("  ✅ Logout screenshot")
    except Exception as e:
        print(f"  ⚠️ {e}")

    # TC-Login-004: Login as regular user
    print("TC-Login-004: Regular user login")
    page.goto(f"{APP_URL}/login", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(2000)
    page.fill("input[type='email']", "johnny@sinopac.com")
    page.fill("input[type='password']", "johnny123")
    page.click("button.login-btn")
    page.wait_for_timeout(5000)
    page.screenshot(path=f"{OUTPUT_DIR}/TC_Login004_user_dashboard.png", full_page=True)
    print(f"  URL: {page.url}")
    print("  ✅ User dashboard screenshot")

    print("\n✅ Login QA complete!")
    browser.close()
