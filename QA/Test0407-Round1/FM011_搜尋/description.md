# FM-011：搜尋

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FM-011 |
| 功能名稱 | 搜尋 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

使用者在搜尋欄輸入關鍵字，系統搜尋符合的檔案和資料夾。

## 測試步驟

1. API：POST `/api/files/search` 帶 `{ path, keyword }` + JWT Token
2. UI：找到搜尋欄位
3. UI：輸入關鍵字「test」
4. UI：按 Enter 執行搜尋
5. 截圖搜尋結果

## 預期結果

- API 回傳 200 及搜尋結果
- UI 搜尋欄可輸入關鍵字，結果正確顯示

## 實際結果

API 回傳 400（請求 body 格式可能不符）。UI 搜尋功能正常，輸入關鍵字後成功顯示搜尋結果。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM011_before_search.png | 搜尋前 | ✅ |
| 002 | screenshots/002_FM011_input_keyword.png | 輸入關鍵字 | ✅ |
| 003 | screenshots/003_FM011_search_result.png | 搜尋結果 | ✅ |

## 狀態判定

❌ FAIL — UI 通過，API 回傳 400（請求格式需確認）

## 備註

需確認 API search 端點預期的 JSON 欄位名稱。
