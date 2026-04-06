# FM-004：移動檔案

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FM-004 |
| 功能名稱 | 移動檔案 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

選取檔案後，可透過「移動」按鈕將檔案移動到其他資料夾。

## 測試步驟

1. API：PATCH `/api/files/move` 帶 `{ sourcePath, destinationPath }` + JWT Token
2. UI：開啟檔案列表
3. UI：嘗試點擊「移動」按鈕
4. UI：等待對話框出現並截圖

## 預期結果

- API 回傳 200，檔案移動成功
- UI 移動對話框正常彈出

## 實際結果

API 回傳 400（請求格式錯誤）。UI「移動」按鈕處於 disabled 狀態（需先勾選檔案 checkbox 才會啟用），Playwright 等待 30 秒後 timeout。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM004_filelist.png | 檔案列表 | ✅ |
| 002 | screenshots/002_FM004_error.png | 按鈕 disabled 錯誤 | ❌ |

## 狀態判定

❌ FAIL — API 回傳 400，UI 按鈕 disabled 未啟用

## 備註

修正方向：UI 測試需先勾選檔案 checkbox 啟用按鈕後再點擊。API 需確認正確的欄位名稱。
