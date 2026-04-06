#!/usr/bin/env python3
"""P003 QA - 最終修正版，JS Interop + 可靠的等待"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

APP_URL = "http://localhost:5000"
BASE_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/test_cases"

def login_and_wait(page):
    """登入並等待首頁完全載入"""
    page.goto(f"{APP_URL}/login", wait_until="networkidle")
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    # 等待跳轉到首頁
    page.wait_for_url(f"{APP_URL}/", timeout=20000)
    # 等待檔案列表（tbody tr）出現，代表 Blazor 已初始化並載入資料
    page.wait_for_selector("tbody tr", timeout=15000)
    # 等待 JS interop 參考設定完成
    page.wait_for_function("() => !!window.blazorComponent", timeout=10000)
    print("  ✅ 登入成功並取得 Blazor 元件參考")

def wait_dialog(page):
    """等待 Radzen 對話框出現"""
    page.wait_for_selector("[role='dialog'], .rz-dialog-content", timeout=10000)
    print("  ✅ 對話框已出現")

def ss(page, path):
    """截圖"""
    page.wait_for_timeout(2000)
    page.screenshot(path=path)
    print(f"  ✅ 截圖: {path.split('/')[-1]}")

def run_test(test_name, dest, screenshot_name, js_invoke_method):
    """執行單個測試案例"""
    print(f"\n--- {test_name} ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        try:
            login_and_wait(page)
            page.evaluate(f"() => window.blazorComponent.invokeMethodAsync('{js_invoke_method}')")
            print(f"  JS -> C#: {js_invoke_method}()")
            wait_dialog(page)
            ss(page, f"{dest}/{screenshot_name}")
        except PlaywrightTimeoutError as e:
            print(f"  ⚠️ Timeout: {e}")
            ss(page, f"{dest}/{screenshot_name}_fail.png")
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            ss(page, f"{dest}/{screenshot_name}_fail.png")
        finally:
            browser.close()

# --- 依序執行所有補測案例 ---
run_test("FM-002: 新增資料夾", f"{BASE_DIR}/FM002_新增資料夾/screenshots", "002_dialog_open_v5.png", "TriggerNewFolderDialog")
run_test("FM-003: 重新命名", f"{BASE_DIR}/FM003_重新命名/screenshots", "002_rename_dialog_v5.png", "TriggerRenameDialog")
run_test("FM-004: 移動", f"{BASE_DIR}/FM004_移動檔案/screenshots", "002_move_dialog_v5.png", "TriggerMoveDialog")
run_test("FM-005: 刪除", f"{BASE_DIR}/FM005_刪除/screenshots", "002_delete_confirm_v5.png", "TriggerDeleteDialog")

print("\n✅ 全部補測完成")
