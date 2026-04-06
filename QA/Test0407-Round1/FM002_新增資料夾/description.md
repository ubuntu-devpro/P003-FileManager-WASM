# FM-002：新增資料夾

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FM-002 |
| 功能名稱 | 新增資料夾 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

使用者點擊「新增」按鈕，彈出對話框輸入資料夾名稱後建立新資料夾。

## 測試步驟

1. API：POST `/api/folders?path=/home/devpro/data&name=...` 帶 JWT Token
2. UI：點擊「新增」按鈕
3. UI：等待對話框出現
4. UI：在對話框內輸入資料夾名稱
5. 截圖記錄

## 預期結果

- API 回傳 200，資料夾建立成功
- UI 對話框正常彈出，可輸入名稱

## 實際結果

API 回傳 200 成功。UI 對話框成功彈出並截圖，但在對話框內定位 input 欄位時失敗——locator 找到了 dialog 容器元素而非內部的 input，導致 `.fill()` 報錯。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM002_before_create.png | 點擊前檔案列表 | ✅ |
| 002 | screenshots/002_FM002_dialog_open.png | 對話框彈出 | ✅ |
| 003 | screenshots/002_FM002_error.png | input 定位錯誤 | ❌ |

## 狀態判定

❌ FAIL — API 通過，UI 對話框內 input 定位失敗

## 備註

問題原因：`DIALOG_SELECTORS` 找到的是 dialog 容器，`.fill()` 無法作用。需改為 `page.locator(".rz-dialog input[type='text']")` 精確定位對話框內的輸入欄位。
