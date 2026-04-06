#!/usr/bin/env python3
"""P003 QA - Playwright E2E Screenshot Test（Blazor WASM，無 SignalR）"""
from playwright.sync_api import sync_playwright
import os

APP_URL = "http://localhost:5000"
OUTPUT_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def screenshot(page, name, wait=2000):
    page.wait_for_timeout(wait)
    page.screenshot(path=f"{OUTPUT_DIR}/{name}", full_page=True)
    print(f"  ✅ {name}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        print(f"\n📸 P003-FileManager-WASM QA 截圖測試")
        print(f"   URL: {APP_URL}")
        print(f"   Output: {OUTPUT_DIR}\n")

        # TC-001: 首頁
        print("TC-001: 首頁截圖")
        page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        screenshot(page, "TC001_homepage.png")

        # TC-002: 檔案列表（首頁已顯示）
        print("TC-002: 檔案列表")
        screenshot(page, "TC002_filelist.png")

        # TC-003: 右鍵選單
        print("TC-003: 右鍵選單")
        try:
            # 找第一個資料夾列
            row = page.locator("tbody tr").first
            row.click(button="right")
            page.wait_for_timeout(1000)
            screenshot(page, "TC003_context_menu.png")
        except Exception as e:
            print(f"  ⚠️ {e}")
            screenshot(page, "TC003_context_menu.png")

        # TC-004: 新增資料夾對話框
        print("TC-004: 新增資料夾對話框")
        try:
            page.click("button:has-text('新增')")
            page.wait_for_timeout(1500)
            screenshot(page, "TC004_new_folder_dialog.png")
            # 關掉對話框
            page.keyboard.press("Escape")
        except Exception as e:
            print(f"  ⚠️ {e}")
            screenshot(page, "TC004_new_folder_dialog.png")

        # TC-005: 搜尋功能
        print("TC-005: 搜尋")
        try:
            search_input = page.locator("input[type='text']").first
            search_input.fill("test")
            page.keyboard.press("Enter")
            page.wait_for_timeout(2000)
            screenshot(page, "TC005_search.png")
            search_input.fill("")
            page.keyboard.press("Enter")
        except Exception as e:
            print(f"  ⚠️ {e}")
            screenshot(page, "TC005_search.png")

        # TC-006: 上傳對話框
        print("TC-006: 上傳對話框")
        try:
            page.click("button:has-text('上傳')")
            page.wait_for_timeout(1500)
            screenshot(page, "TC006_upload_dialog.png")
            page.keyboard.press("Escape")
        except Exception as e:
            print(f"  ⚠️ {e}")
            screenshot(page, "TC006_upload_dialog.png")

        # TC-007: 設定頁面（如果有的話）
        print("TC-007: 設定頁面")
        try:
            settings = page.locator("a:has-text('設定'), button:has-text('設定')")
            if settings.count() > 0:
                settings.first.click()
                page.wait_for_timeout(2000)
                screenshot(page, "TC007_settings.png")
            else:
                print("  ⏭️ 設定頁面不存在")
        except Exception as e:
            print(f"  ⚠️ {e}")

        print(f"\n✅ 截圖完成")
        print(f"   目錄: {OUTPUT_DIR}")

        browser.close()

if __name__ == "__main__":
    main()
