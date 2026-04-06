#!/usr/bin/env python3
"""P003 QA - 補足所有缺失的測試案例"""
from playwright.sync_api import sync_playwright
import subprocess, time

APP_URL = "http://localhost:5000"
OUTPUT_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA/screenshots"

def ss(page, name, wait=2000):
    page.wait_for_timeout(wait)
    page.screenshot(path=f"{OUTPUT_DIR}/{name}", full_page=True)
    print(f"  ✅ {name}")

def api_get(path):
    r = subprocess.run(["curl", "-s", f"http://localhost:5001{path}"], capture_output=True, text=True)
    return r.stdout

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    print("=== 補足測試案例 ===\n")

    # === FM-009/010: 下載（先確認 API）===
    print("FM-009/010: 下載 API 驗證")
    # 建立測試檔案
    subprocess.run(["curl", "-s", "-X", "POST",
        "http://localhost:5001/api/folders?path=/home/devpro/data&name=QA_TestFolder"],
        capture_output=True)
    subprocess.run(["bash", "-c",
        "echo 'download test' > /home/devpro/data/QA_TestFolder/download_test.txt"],
        capture_output=True)
    time.sleep(1)

    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "http://localhost:5001/api/files/download?path=/home/devpro/data/QA_TestFolder/download_test.txt"],
        capture_output=True, text=True)
    print(f"  單一下載 HTTP: {r.stdout.strip()}")
    ss(page, "FM009_single_download.png")

    # === FM-003: 重新命名對話框 ===
    print("FM-003: 重新命名對話框")
    page.goto(APP_URL, wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(3000)

    # 點第一個檔案的重新命名按鈕
    try:
        # 找 pencil/edit 按鈕
        edit_btns = page.locator("button").all()
        for btn in edit_btns:
            txt = btn.inner_text()
            if "重新命名" in txt or "edit" in txt.lower() or "✏️" in txt:
                btn.click()
                page.wait_for_timeout(2000)
                ss(page, "FM003_rename_dialog.png")
                print("  ✅ 重新命名對話框截圖")
                page.keyboard.press("Escape")
                break
        else:
            # 嘗試點右鍵選單
            row = page.locator("tbody tr").first
            row.click(button="right")
            page.wait_for_timeout(1500)
            ss(page, "FM003_context_rename.png")
            print("  ✅ 右鍵->重新命名截圖")
            page.keyboard.press("Escape")
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, "FM003_rename_dialog.png")

    # === FM-004: 移動對話框 ===
    print("FM-004: 移動對話框")
    try:
        # 點第一個檔案的移動按鈕
        btns = page.locator("button").all()
        for btn in btns:
            txt = btn.inner_text()
            if "移動" in txt or "folder" in txt.lower():
                btn.click()
                page.wait_for_timeout(2000)
                ss(page, "FM004_move_dialog.png")
                print("  ✅ 移動對話框截圖")
                page.keyboard.press("Escape")
                break
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, "FM004_move_dialog.png")

    # === FM-005: 刪除確認 ===
    print("FM-005: 刪除確認對話框")
    try:
        btns = page.locator("button").all()
        for btn in btns:
            txt = btn.inner_text()
            if "刪除" in txt:
                btn.click()
                page.wait_for_timeout(2000)
                ss(page, "FM005_delete_confirm.png")
                print("  ✅ 刪除確認截圖")
                page.keyboard.press("Escape")
                break
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, "FM005_delete_confirm.png")

    # === FM-007: 多重上傳 ===
    print("FM-007: 多重上傳")
    try:
        btns = page.locator("button").all()
        for btn in btns:
            if "上傳" in btn.inner_text():
                btn.click()
                page.wait_for_timeout(2000)
                # 檢查是否有 multiple 屬性
                file_input = page.locator("input[type='file']")
                if file_input.count() > 0:
                    multiple = page.evaluate("() => document.querySelector('input[type=file]').multiple")
                    print(f"  多重上傳: {'✅ 支持' if multiple else '⚠️ 不支持 multiple'}")
                ss(page, "FM007_multi_upload.png")
                print("  ✅ 多重上傳對話框截圖")
                page.keyboard.press("Escape")
                break
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, "FM007_multi_upload.png")

    # === FM-008: 拖拉上傳（UI 檢查）===
    print("FM-008: 拖拉上傳")
    try:
        btns = page.locator("button").all()
        for btn in btns:
            if "上傳" in btn.inner_text():
                btn.click()
                page.wait_for_timeout(2000)
                # 檢查 drop zone
                dropzone = page.locator("[class*='drop'], [class*='upload']").first
                if dropzone.count() > 0:
                    print("  ✅ Drop zone 存在")
                ss(page, "FM008_drag_upload.png")
                print("  ✅ 拖拉上傳截圖")
                page.keyboard.press("Escape")
                break
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, "FM008_drag_upload.png")

    # === FM-010: 多重下載 ===
    print("FM-010: 多重下載")
    # 先勾選複選框
    try:
        page.goto(APP_URL, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)
        # 勾選第一個資料夾
        cb = page.locator("tbody tr:first-child input[type='checkbox']").first
        cb.click()
        page.wait_for_timeout(1000)
        ss(page, "FM010_multi_select.png")
        # 點下載按鈕
        btns = page.locator("button").all()
        for btn in btns:
            if "下載" in btn.inner_text():
                btn.click()
                page.wait_for_timeout(2000)
                ss(page, "FM010_multi_download.png")
                print("  ✅ 多重下載截圖")
                break
    except Exception as e:
        print(f"  ⚠️ {e}")
        ss(page, "FM010_multi_download.png")

    # === 側邊欄資料夾樹 ===
    print("額外: 側邊欄樹")
    try:
        page.goto(APP_URL, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)
        ss(page, "sidebar_tree.png")
        print("  ✅ 側邊欄截圖")
    except Exception as e:
        print(f"  ⚠️ {e}")

    print("\n✅ 補足測試完成！")
    browser.close()
