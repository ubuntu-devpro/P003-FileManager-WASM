#!/usr/bin/env python3
"""P003 QA - 最終版，用 JS Interop 直接呼叫 C# 方法"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

APP_URL = "http://localhost:5000"
BASE_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/test_cases"

def login_and_wait(page):
    page.goto(f"{APP_URL}/login", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    page.wait_for_url(f"{APP_URL}/", timeout=15000)
    page.wait_for_timeout(5000)  # Wait for Blazor to initialize
    # Verify we have the dotnet reference
    component_exists = page.evaluate("() => !!window.blazorComponent")
    if not component_exists:
        raise Exception("Blazor component reference not found!")
    print("  ✅ 登入並取得 Blazor 元件參考")

def wait_dialog(page, timeout=10000):
    page.wait_for_selector("[role='dialog'], .rz-dialog-content", timeout=timeout)
    print("  ✅ 對話框已出現")

def ss(page, path):
    page.wait_for_timeout(2000)
    page.screenshot(path=path, full_page=True)
    print(f"  ✅ 截圖: {path.split('/')[-1]}")

def run_test(test_name, dest, screenshot_name, js_invoke_method):
    print(f"\n--- {test_name} ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        try:
            login_and_wait(page)
            # Invoke C# method from JS
            page.evaluate(f"() => window.blazorComponent.invokeMethodAsync('{js_invoke_method}')")
            print(f"  JS -> C#: {js_invoke_method}()")
            wait_dialog(page)
            ss(page, f"{dest}/{screenshot_name}")
        except PlaywrightTimeoutError:
            print(f"  ⚠️ Timeout: 對話框未在指定時間內出現")
            ss(page, f"{dest}/{screenshot_name}_fail.png")
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            ss(page, f"{dest}/{screenshot_name}_fail.png")
        finally:
            browser.close()

# --- 執行測試 ---
run_test("FM-002: 新增資料夾", f"{BASE_DIR}/FM002_新增資料夾/screenshots", "002_dialog_open_v4.png", "TriggerNewFolderDialog")
run_test("FM-003: 重新命名", f"{BASE_DIR}/FM003_重新命名/screenshots", "002_rename_dialog_v4.png", "TriggerRenameDialog")
run_test("FM-004: 移動", f"{BASE_DIR}/FM004_移動檔案/screenshots", "002_move_dialog_v4.png", "TriggerMoveDialog")
run_test("FM-005: 刪除", f"{BASE_DIR}/FM005_刪除/screenshots", "002_delete_confirm_v4.png", "TriggerDeleteDialog")

print("\n✅ 全部完成")
