# FM-001：資料夾瀏覽

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FM-001 |
| 功能名稱 | 資料夾瀏覽 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

使用者登入後可瀏覽 RootFolder（/home/devpro/data）下的檔案和資料夾列表。

## 測試步驟

1. API：GET `/api/files?path=/home/devpro/data` 帶 JWT Token
2. UI：登入後確認首頁顯示檔案列表
3. 確認檔案列表表格元件存在

## 預期結果

- API 回傳 200 及檔案列表 JSON
- UI 顯示資料夾和檔案的表格

## 實際結果

API 回傳 200，UI 正確顯示檔案列表表格。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM001_homepage.png | 首頁 | ✅ |
| 002 | screenshots/002_FM001_filelist.png | 檔案列表 | ✅ |

## 狀態判定

✅ PASS — API 與 UI 均符合預期

## 備註

無
