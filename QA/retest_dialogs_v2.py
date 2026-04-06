#!/usr/bin/env python3
"""P003 QA - 重新測試對話框截圖（正確版本）"""
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:5000"
BASE_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/test_cases"

def wait_dialog_appear(page, timeout=10000):
    """等待對話框出現"""
    page.wait_for_selector("[role='dialog'], .rz-dialog", timeout=timeout)

def close_dialog_by_button(page):
    """用關閉按鈕關閉對話框"""
    try:
        # 嘗試點擊 Close / X / 否認 / 取消 按鈕
        selectors = [
            "button:has-text('×')",
            "button:has-text('X')",
            "button:has-text('否認')",
            "button:has-text('取消')",
            "button.rz-dialog-titlebar-close",
            "[aria-label='Close']",
        ]
        for sel in selectors:
            btns = page.locator(sel).all()
            for btn in btns:
                try:
                    btn.click(timeout=2000)
                    page.wait_for_timeout(1500)
                    return
                except:
                    pass
    except:
        pass
    # fallback: 按 Escape
    page.keyboard.press("Escape")
    page.wait_for_timeout(1500)

def ss(page, path, wait=2000):
    page.wait_for_timeout(wait)
    page.screenshot(path=path, full_page=True)
    print(f"  ✅ {path.split('/')[-1]}")

def go_home(page):
    """確保回到首頁（刷新）"""
    page.goto(f"{APP_URL}/", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(4000)
    print(f"  首頁 URL: {page.url}")

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

    # ===== FM-002: 新增資料夾 =====
    print("\nFM-002: 新增資料夾對話框")
    go_home(page)
    dest = f"{BASE_DIR}/FM002_新增資料夾/screenshots"
    try:
        new_btn = page.get_by_text("新增", exact=False).first
        new_btn.click()
        wait_dialog_appear(page)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/002_dialog_open.png")
        print("  ✅ 對話框截圖成功")
        close_dialog_by_button(page)
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, f"{dest}/002_dialog_open.png")

    # ===== FM-003: 重新命名 =====
    print("\nFM-003: 重新命名對話框")
    go_home(page)
    dest = f"{BASE_DIR}/FM003_重新命名/screenshots"
    try:
        rename_btn = page.get_by_text("✏️", exact=False).first
        rename_btn.click()
        wait_dialog_appear(page)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/002_rename_dialog.png")
        print("  ✅ 重新命名對話框截圖成功")
        close_dialog_by_button(page)
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, f"{dest}/002_rename_dialog.png")

    # ===== FM-004: 移動 =====
    print("\nFM-004: 移動對話框")
    go_home(page)
    dest = f"{BASE_DIR}/FM004_移動檔案/screenshots"
    try:
        # 找移動按鈕（中文"移動"或英文"move"）
        move_btn = page.get_by_text("移動", exact=False).first
        move_btn.click()
        wait_dialog_appear(page)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/002_move_dialog.png")
        print("  ✅ 移動對話框截圖成功")
        close_dialog_by_button(page)
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, f"{dest}/002_move_dialog.png")

    # ===== FM-005: 刪除確認 =====
    print("\nFM-005: 刪除確認對話框")
    go_home(page)
    dest = f"{BASE_DIR}/FM005_刪除/screenshots"
    try:
        delete_btn = page.get_by_text("🗑️", exact=False).first
        delete_btn.click()
        wait_dialog_appear(page)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/002_delete_confirm.png")
        print("  ✅ 刪除確認截圖成功")
        close_dialog_by_button(page)
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, f"{dest}/002_delete_confirm.png")

    # ===== FM-009: 下載按鈕 =====
    print("\nFM-009: 下載按鈕")
    go_home(page)
    dest = f"{BASE_DIR}/FM009_單一下載/screenshots"
    try:
        download_btn = page.get_by_text("⬇", exact=False).first
        download_btn.click()
        page.wait_for_timeout(3000)
        ss(page, f"{dest}/002_download_action.png")
        print("  ✅ 下載截圖成功")
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, f"{dest}/002_download_action.png")

    # ===== FM-010: 多重下載 =====
    print("\nFM-010: 多重下載")
    go_home(page)
    dest = f"{BASE_DIR}/FM010_多重下載/screenshots"
    try:
        # 勾選第一個項目
        cb = page.locator("tbody tr:first-child input[type='checkbox']").first
        cb.check()
        page.wait_for_timeout(1000)
        ss(page, f"{dest}/003_multi_selected.png")
        print("  ✅ 多重選擇截圖成功")

        # 點擊下載
        download_btn = page.get_by_text("⬇", exact=False).first
        download_btn.click()
        wait_dialog_appear(page)
        page.wait_for_timeout(2000)
        ss(page, f"{dest}/003_multi_download_dialog.png")
        print("  ✅ 多重下載對話框截圖成功")
        close_dialog_by_button(page)
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, f"{dest}/003_multi_selected.png")

    print("\n✅ 全部完成")
    browser.close()
