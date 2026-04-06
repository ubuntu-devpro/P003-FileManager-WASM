# FA-004：Session驗證

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FA-004 |
| 功能名稱 | Session驗證 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

驗證使用者登入後的 Session 是否有效，確保 API 能正確識別已登入的使用者。

## 測試步驟

1. 登入取得 JWT Token
2. API 測試：GET /api/auth/session，帶入 Token
3. 確認回傳 200，Session 有效

## 預期結果

- API 回傳 200，確認 Session 有效

## 實際結果

API 回傳 200，Session 驗證成功，Token 有效。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| — | — | 無專屬 UI，僅 API 驗證 | — |

## 狀態判定

- ✅ PASS — API 驗證通過

## 備註

本測試案例無專屬 UI 畫面，僅透過 API 驗證 Session 有效性。
