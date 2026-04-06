#!/usr/bin/env python3
"""P003 QA - 每個測試用新分頁，隔離狀態"""
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"
BASE_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/test_cases"

def wait_dialog(page, timeout=10000):
    page.wait_for_selector("[role='dialog'], .rz-dialog", timeout=timeout)

def ss(page, path):
    page.wait_for_timeout(2000)
    page.screenshot(path=path, full_page=True)
    print(f"  ✅ {path.split('/')[-1]}")

def login_and_go_home(page):
    """登入並到首頁"""
    page.goto(f"{APP_URL}/login", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    page.wait_for_timeout(5000)
    # 等首頁檔案列表出現
    page.wait_for_selector("tbody tr", timeout=10000)
    page.wait_for_timeout(2000)

def test_new_page(test_name, dest, screenshot_name, action_fn):
    """每個測試用新分頁"""
    with p.chromium.launch(headless=True) as browser:
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        login_and_go_home(page)
        try:
            action_fn(page)
            wait_dialog(page)
            page.wait_for_timeout(2000)
            ss(page, f"{dest}/{screenshot_name}")
            print(f"  ✅ {test_name} 成功")
        except Exception as e:
            print(f"  ⚠️ {test_name}: {e}")
            ss(page, f"{dest}/{screenshot_name}")
        ctx.close()

with sync_playwright() as p:
    print("FM-002: 新增資料夾對話框")
    test_new_page(
        "FM-002",
        f"{BASE_DIR}/FM002_新增資料夾/screenshots",
        "002_dialog_open.png",
        lambda page: page.get_by_text("新增", exact=False).first.click()
    )

    print("FM-003: 重新命名對話框")
    test_new_page(
        "FM-003",
        f"{BASE_DIR}/FM003_重新命名/screenshots",
        "002_rename_dialog.png",
        lambda page: page.get_by_text("✏️", exact=False).first.click()
    )

    print("FM-004: 移動對話框")
    test_new_page(
        "FM-004",
        f"{BASE_DIR}/FM004_移動檔案/screenshots",
        "002_move_dialog.png",
        lambda page: page.get_by_text("移動", exact=False).first.click()
    )

    print("FM-005: 刪除確認對話框")
    test_new_page(
        "FM-005",
        f"{BASE_DIR}/FM005_刪除/screenshots",
        "002_delete_confirm.png",
        lambda page: page.get_by_text("🗑️", exact=False).first.click()
    )

    print("FM-009: 下載按鈕")
    with p.chromium.launch(headless=True) as browser:
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        login_and_go_home(page)
        try:
            page.get_by_text("⬇", exact=False).first.click()
            page.wait_for_timeout(3000)
            ss(page, f"{BASE_DIR}/FM009_單一下載/screenshots/002_download_action.png")
            print("  ✅ FM-009 成功")
        except Exception as e:
            print(f"  ⚠️ FM-009: {e}")
            ss(page, f"{BASE_DIR}/FM009_單一下載/screenshots/002_download_action.png")
        ctx.close()

    print("FM-010: 多重下載")
    with p.chromium.launch(headless=True) as browser:
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        login_and_go_home(page)
        try:
            page.locator("tbody tr:first-child input[type='checkbox']").first.check()
            page.wait_for_timeout(1000)
            ss(page, f"{BASE_DIR}/FM010_多重下載/screenshots/003_multi_selected.png")
            page.get_by_text("⬇", exact=False).first.click()
            wait_dialog(page)
            page.wait_for_timeout(2000)
            ss(page, f"{BASE_DIR}/FM010_多重下載/screenshots/003_multi_download_dialog.png")
            print("  ✅ FM-010 成功")
        except Exception as e:
            print(f"  ⚠️ FM-010: {e}")
            ss(page, f"{BASE_DIR}/FM010_多重下載/screenshots/003_multi_selected.png")
        ctx.close()

print("\n✅ 全部完成")
