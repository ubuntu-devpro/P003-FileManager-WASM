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

使用者可透過搜尋欄位輸入關鍵字搜尋檔案。

## 測試步驟

1. API 測試：POST /api/files/search，傳送 {path, query}
2. UI 測試：找到搜尋輸入欄位
3. 輸入關鍵字 "test"
4. 按下 Enter
5. 確認搜尋結果顯示

## 預期結果

- API 回傳 200，包含搜尋結果
- UI 搜尋欄位可輸入關鍵字，按 Enter 後顯示搜尋結果

## 實際結果

API 回傳 200，成功取得搜尋結果。UI 搜尋欄位正常，輸入 "test" 並按 Enter 後，搜尋結果正確顯示。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM011_before_search.png | 搜尋前畫面 | ✅ |
| 002 | screenshots/002_FM011_input_keyword.png | 輸入搜尋關鍵字 | ✅ |
| 003 | screenshots/003_FM011_search_result.png | 搜尋結果 | ✅ |

## 狀態判定

- ✅ PASS — 截圖符合預期結果

## 備註

無
