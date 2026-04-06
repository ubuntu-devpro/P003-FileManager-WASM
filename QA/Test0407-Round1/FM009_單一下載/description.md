# FM-009：單一下載

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FM-009 |
| 功能名稱 | 單一下載 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

使用者可下載單一檔案。

## 測試步驟

1. 建立測試檔案 `/home/devpro/data/qa_download_test.txt`
2. API：GET `/api/files/download?path=...` 帶 JWT Token
3. UI：確認下載按鈕存在並截圖

## 預期結果

- API 回傳 200 及檔案內容
- UI 下載按鈕可見

## 實際結果

API 回傳 200，檔案下載成功。UI 下載按鈕正常顯示。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FM009_filelist.png | 檔案列表 | ✅ |
| 002 | screenshots/002_FM009_download_button.png | 下載按鈕 | ✅ |

## 狀態判定

✅ PASS — API 與 UI 均符合預期

## 備註

無
