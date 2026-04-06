#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    
    print("Navigating to login...")
    page.goto(f"{APP_URL}/login", wait_until="networkidle")
    print(f"URL: {page.url}")
    
    print("Logging in...")
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    
    print("Waiting for navigation to /")
    try:
        page.wait_for_url(f"{APP_URL}/", timeout=20000)
        print(f"SUCCESS: Navigated to {page.url}")
    except Exception as e:
        print(f"FAILURE: Did not navigate. Current URL: {page.url}")
        print(e)
    
    page.screenshot(path="/tmp/final_login_test.png")
    browser.close()
