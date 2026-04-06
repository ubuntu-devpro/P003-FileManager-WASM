# FM-006：單一上傳

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FM-006 |
| 功能名稱 | 單一上傳 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

使用者點擊「上傳」按鈕，選擇單一檔案上傳至目前資料夾。

## 測試步驟

1. API：POST `/api/upload?path=/home/devpro/data` 帶檔案 + JWT Token
2. UI：點擊「上傳」按鈕
3. UI：確認上傳對話框或 file input 出現

## 預期結果

- API 回傳 200，檔案上傳成功
- UI 上傳對話框正常顯示

## 實際結果

API 回傳 200 成功。UI 上傳按鈕點擊後對話框正常彈出，file input 元件存在。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM006_before_upload.png | 上傳前畫面 | ✅ |
| 002 | screenshots/002_FM006_upload_dialog.png | 上傳對話框 | ✅ |

## 狀態判定

✅ PASS — API 與 UI 均符合預期

## 備註

無
