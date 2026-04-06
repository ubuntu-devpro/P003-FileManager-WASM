# P003-FileManager-WASM Playwright 測試計畫 v2

**建立日期：** 2026-04-07
**測試人員：** 龍叔（Claude）
**工具：** Playwright (Python sync API)
**測試環境：** Ubuntu-Devpro（VM）
**應用 URL：** Client http://localhost:5000 / API http://localhost:5001

---

## 1. 測試範圍

### 檔案管理功能（FM-001 ~ FM-011）

| 編號 | 功能 | 測試類型 | 上次狀態 | 本次改進 |
|------|------|----------|----------|----------|
| FM-001 | 資料夾瀏覽 | API + UI | ✅ PASS | 維持 |
| FM-002 | 新增資料夾 | API + UI | ❌ FAIL | 加入 `wait_for_selector` 等待對話框 |
| FM-003 | 重新命名 | API + UI | ❌ FAIL | 同上 |
| FM-004 | 移動檔案 | API + UI | ❌ FAIL | 同上 |
| FM-005 | 刪除 | API + UI | ❌ FAIL | 同上 |
| FM-006 | 單一上傳 | API + UI | ✅ PASS | 維持 |
| FM-007 | 多重上傳 | API + UI | ✅ PASS | 維持 |
| FM-008 | 拖拉上傳 | UI 檢查 | ✅ PASS | 維持 |
| FM-009 | 單一下載 | API + UI | ❌ FAIL | 確保頁面穩定後再截圖 |
| FM-010 | 多重下載 | API + UI | ⚠️ 部分 | 改善選取 + 下載流程 |
| FM-011 | 搜尋 | API + UI | ✅ PASS | 維持 |

### 認證功能（FA-001 ~ FA-004）

| 編號 | 功能 | 測試類型 | 上次狀態 | 本次改進 |
|------|------|----------|----------|----------|
| FA-001 | 使用者登入 | API + UI | ✅ PASS | 維持 |
| FA-002 | 多網域權限 | API + UI | ✅ PASS | 維持 |
| FA-003 | 登出 | API + UI | ✅ PASS | 維持 |
| FA-004 | Session 驗證 | API | ✅ PASS | 維持 |

---

## 2. 測試策略

### 2.1 對話框截圖修正策略

上次失敗的主因：Blazor WASM Dialog 元件點擊後需時間 render DOM，Playwright 在對話框出現前就截圖了。

**解決方案：**
```python
# 點擊觸發對話框的按鈕後，明確等待對話框 DOM 出現
page.wait_for_selector('.rz-dialog, [role="dialog"], .modal', timeout=5000)
```

### 2.2 截圖等待策略

| 情境 | 等待方式 |
|------|----------|
| 頁面導航 | `wait_until="networkidle"` |
| 對話框彈出 | `wait_for_selector` 指定對話框選擇器 |
| API 回應後 UI 更新 | `wait_for_timeout(2000)` + `wait_for_selector` |
| 下載觸發 | 監聽 `download` 事件 |

### 2.3 API 測試端點

| # | 測試項目 | Method | Endpoint |
|---|---------|--------|----------|
| 1 | Admin 登入 | POST | `/api/auth/login` |
| 2 | 一般使用者登入 | POST | `/api/auth/login` |
| 3 | Session 驗證 | GET | `/api/auth/session` |
| 4 | 列出檔案 | GET | `/api/files?path=/home/devpro/data` |
| 5 | 搜尋 | POST | `/api/files/search` |
| 6 | 建立資料夾 | POST | `/api/folders?path=...&name=...` |
| 7 | 重新命名 | PATCH | `/api/files/rename` |
| 8 | 移動 | PATCH | `/api/files/move` |
| 9 | 上傳 | POST | `/api/upload` |
| 10 | 下載 | GET | `/api/files/download?path=...` |
| 11 | 刪除 | DELETE | `/api/files` |

---

## 3. 截圖命名規範

遵循 QA-003 規範：
```
{編號}_{功能編號}_{描述}.png

例：
001_FM001_homepage.png
002_FM002_click_new_folder.png
003_FM002_dialog_open.png
004_FM002_input_name.png
005_FM002_folder_created.png
```

---

## 4. 測試腳本

主腳本：`QA/p003_playwright_test_v2.py`

### 執行前提
1. Server 已啟動：`cd src/Server && dotnet run --urls "http://localhost:5001"`
2. Client 已啟動：`cd src/Client && dotnet run`
3. Playwright 已安裝：`pip install playwright && playwright install chromium`

### 執行方式
```bash
cd ~/Claude-Workspace/projects/P003-FileManager-WASM
python3 QA/p003_playwright_test_v2.py
```

---

## 5. 輸出

- 截圖：`QA/test_cases/{功能編號}_{功能名稱}/screenshots/`
- 測試結果 JSON：`QA/test_result_v2.json`
- 測試結束後更新 `QA/test_summary.md`

---

_最後更新：2026-04-07_
