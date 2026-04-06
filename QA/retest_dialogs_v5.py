#!/usr/bin/env python3
"""P003 QA - 對話框截圖，使用 JSInterop 直接觸發 Blazor 方法"""
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"
BASE_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/test_cases"
OUT_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/screenshots/dialogs_v5"

import os
os.makedirs(OUT_DIR, exist_ok=True)

def login(page):
    page.goto(f"{APP_URL}/login", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    page.wait_for_timeout(6000)
    page.wait_for_selector("tbody tr", timeout=10000)
    page.wait_for_timeout(2000)

def ss(page, path):
    page.wait_for_timeout(2000)
    page.screenshot(path=path, full_page=True)

def wait_dialog(page):
    page.wait_for_selector("[role='dialog'], .rz-dialog, .dialog-overlay", timeout=10000)

def invoke_blazor(page, method_name):
    """直接用 JSInterop 叫 Blazor 的 [JSInvokable] 方法"""
    return page.evaluate(f"""
        window.blazorComponent.invokeMethodAsync('{method_name}')
    """)

def click_and_wait_dialog(page, selector):
    """傳統 DOM click，嘗試等待對話框"""
    page.click(selector, timeout=5000)
    page.wait_for_timeout(2000)

def new_page_test(name, dest_file, trigger_fn):
    """用 JSInterop 觸發對話框並截圖"""
    print(f"\n{name}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()

        login(page)

        # 確保 blazorComponent 已設定
        page.wait_for_timeout(2000)

        try:
            trigger_fn(page)
            wait_dialog(page)
            page.wait_for_timeout(2000)
            ss(page, f"{OUT_DIR}/{dest_file}")
            print(f"  ✅ {name} 成功")
        except Exception as e:
            print(f"  ⚠️ {name}: {e}")
            ss(page, f"{OUT_DIR}/{dest_file}")

        ctx.close()

# ============================================================
# 測試案例
# ============================================================

# FM-002: 新增資料夾
new_page_test(
    "FM-002 新增資料夾",
    "FM-002_new_folder_dialog.png",
    lambda page: invoke_blazor(page, "TriggerNewFolderDialog")
)

# FM-003: 重新命名（需要先選取一個檔案）
def trigger_rename(page):
    # 先選取第一個檔案（點擊 checkbox）
    checkbox = page.locator("tbody tr:first-child input[type='checkbox']")
    if checkbox.count() > 0:
        checkbox.first.click()
        page.wait_for_timeout(500)
    invoke_blazor(page, "TriggerRenameDialog")

new_page_test(
    "FM-003 重新命名",
    "FM-003_rename_dialog.png",
    trigger_rename
)

# FM-005: 刪除確認（先選取檔案）
def trigger_delete(page):
    checkbox = page.locator("tbody tr:first-child input[type='checkbox']")
    if checkbox.count() > 0:
        checkbox.first.click()
        page.wait_for_timeout(500)
    # 找刪除按鈕並點擊
    delete_btn = page.locator("button:has-text('刪除'), .fm-toolbar button:nth-child(4)")
    if delete_btn.count() > 0:
        delete_btn.first.click()
    page.wait_for_timeout(2000)

new_page_test(
    "FM-005 刪除確認",
    "FM-005_delete_dialog.png",
    trigger_delete
)

# FM-004: 移動（先選取檔案）
def trigger_move(page):
    checkbox = page.locator("tbody tr:first-child input[type='checkbox']")
    if checkbox.count() > 0:
        checkbox.first.click()
        page.wait_for_timeout(500)
    invoke_blazor(page, "TriggerMoveDialog")

new_page_test(
    "FM-004 移動",
    "FM-004_move_dialog.png",
    trigger_move
)

print(f"\n✅ 全部完成，截圖保存在: {OUT_DIR}")
