#!/usr/bin/env python3
"""P003 - Quick homepage test"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto("http://localhost:5000", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(5000)
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")
    page.screenshot(path="/tmp/p003_home.png", full_page=True)
    # Get console errors
    errors = page.evaluate("() => window.__blazorErrors = window.__blazorErrors || []; return window.__blazorErrors")
    print(f"Errors captured: {errors}")
    browser.close()
