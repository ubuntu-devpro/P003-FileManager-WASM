#!/usr/bin/env python3
"""P003 QA - 重新測試失敗的對話框截圖（使用 wait_for_selector）"""
from playwright.sync_api import sync_playwright
import time

APP_URL = "http://localhost:5000"
BASE_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/test_cases"

def ss(page, path, wait=2000):
    page.wait_for_timeout(wait)
    page.screenshot(path=path, full_page=True)
    print(f"  ✅ {path.split('/')[-1]}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    # ===== 先登入 =====
    print("0. 登入...")
    page.goto(f"{APP_URL}/login", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)
    page.fill("input[type='email']", "admin@devpro.com.tw")
    page.fill("input[type='password']", "admin123")
    page.click("button.login-btn")
    page.wait_for_timeout(5000)
    print(f"  登入後 URL: {page.url}")

    # ===== FM-002: 新增資料夾對話框 =====
    print("\nFM-002: 新增資料夾對話框")
    dest = f"{BASE_DIR}/FM002_新增資料夾/screenshots"
    try:
        # 點擊新增按鈕，等待對話框出現
        new_folder_btn = page.get_by_text("新增", exact=False).first
        new_folder_btn.click()
        # 等待對話框出現（最多10秒）
        page.wait_for_selector("[role='dialog'], .rz-dialog, .dialog-content",
                              timeout=10000)
        page.wait_for_timeout(2000)  # 額外等待 DOM render
        ss(page, f"{dest}/002_dialog_open.png")
        print("  ✅ 對話框截圖成功")
    except Exception as e:
        print(f"  ⚠️ 失敗: {e}")
        ss(page, f"{dest}/002_dialog_open.png")  # 截圖現狀

    # 按 Escape 關閉
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    # ===== FM-003: 重新命名對話框 =====
    print("\nFM-003: 重新命名對話框")
    dest = f"{BASE_DIR}/FM003_重新命名/screenshots"
    try:
        # 點第一個檔案的重新命名按鈕
        rename_btn = page.get_by_text("✏️", exact=False).first
        rename_btn.click()
        page.wait_for_selector("[role='dialog'], .rz-dialog",
                              timeout=10000)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/002_rename_dialog.png")
        print("  ✅ 重新命名對話框截圖成功")
    except Exception as e:
        print(f"  ⚠️ 失敗: {e}")
        ss(page, f"{dest}/002_rename_dialog.png")

    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    # ===== FM-004: 移動對話框 =====
    print("\nFM-004: 移動對話框")
    dest = f"{BASE_DIR}/FM004_移動檔案/screenshots"
    try:
        # 點第一個檔案的移動按鈕
        move_btn = page.get_by_text("移", exact=False).first
        move_btn.click()
        page.wait_for_selector("[role='dialog'], .rz-dialog",
                              timeout=10000)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/002_move_dialog.png")
        print("  ✅ 移動對話框截圖成功")
    except Exception as e:
        print(f"  ⚠️ 失敗: {e}")
        ss(page, f"{dest}/002_move_dialog.png")

    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    # ===== FM-005: 刪除確認對話框 =====
    print("\nFM-005: 刪除確認對話框")
    dest = f"{BASE_DIR}/FM005_刪除/screenshots"
    try:
        delete_btn = page.get_by_text("🗑️", exact=False).first
        delete_btn.click()
        page.wait_for_selector("[role='dialog'], .rz-dialog, .confirm",
                              timeout=10000)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/002_delete_confirm.png")
        print("  ✅ 刪除確認對話框截圖成功")
    except Exception as e:
        print(f"  ⚠️ 失敗: {e}")
        ss(page, f"{dest}/002_delete_confirm.png")

    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    # ===== FM-009: 下載 =====
    print("\nFM-009: 下載")
    dest = f"{BASE_DIR}/FM009_單一下載/screenshots"
    try:
        download_btn = page.get_by_text("⬇", exact=False).first
        download_btn.click()
        page.wait_for_timeout(3000)
        ss(page, f"{dest}/002_download_action.png")
        print("  ✅ 下載截圖成功")
    except Exception as e:
        print(f"  ⚠️ 失敗: {e}")
        ss(page, f"{dest}/002_download_action.png")

    # ===== FM-010: 多重下載對話框 =====
    print("\nFM-010: 多重下載")
    dest = f"{BASE_DIR}/FM010_多重下載/screenshots"
    try:
        # 先勾選第一個項目
        cb = page.locator("tbody tr:first-child input[type='checkbox']").first
        cb.check()
        page.wait_for_timeout(1000)
        ss(page, f"{dest}/003_multi_selected.png")
        print("  ✅ 多重選擇截圖成功")

        # 點擊下載
        download_btn = page.get_by_text("⬇", exact=False).first
        download_btn.click()
        page.wait_for_selector("[role='dialog'], .rz-dialog",
                              timeout=10000)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/003_multi_download_dialog.png")
        print("  ✅ 多重下載對話框截圖成功")
    except Exception as e:
        print(f"  ⚠️ 失敗: {e}")
        ss(page, f"{dest}/003_multi_selected.png")

    print("\n✅ 補測完成")
    browser.close()
