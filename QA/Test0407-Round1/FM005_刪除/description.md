# FM-005：刪除

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FM-005 |
| 功能名稱 | 刪除 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

選取檔案或資料夾後，點擊「刪除」按鈕彈出確認對話框，確認後刪除。

## 測試步驟

1. API：DELETE `/api/files` 帶 `{ path }` + JWT Token
2. UI：開啟檔案列表
3. UI：嘗試點擊「刪除」按鈕
4. UI：等待確認對話框出現並截圖

## 預期結果

- API 回傳 200，檔案刪除成功
- UI 確認對話框正常彈出

## 實際結果

API 回傳 400（請求格式錯誤）。UI「刪除」按鈕處於 disabled 狀態（需先勾選檔案 checkbox 才會啟用），Playwright 等待 30 秒後 timeout。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM005_filelist.png | 檔案列表 | ✅ |
| 002 | screenshots/002_FM005_error.png | 按鈕 disabled 錯誤 | ❌ |

## 狀態判定

❌ FAIL — API 回傳 400，UI 按鈕 disabled 未啟用

## 備註

修正方向：同 FM-004，UI 測試需先勾選檔案 checkbox 啟用按鈕。API 需確認正確的請求格式。
