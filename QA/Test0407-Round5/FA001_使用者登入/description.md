# FA-001：使用者登入

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FA-001 |
| 功能名稱 | 使用者登入 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

使用者透過 Email 和密碼登入系統，取得 JWT Token 以進行後續操作。

## 測試步驟

1. API 測試：POST /api/auth/login，傳送帳號密碼
2. UI 測試：開啟登入頁面，確認有 email/password 輸入欄位
3. 輸入 admin@devpro.com.tw 及密碼
4. 點擊登入按鈕
5. 確認登入成功

## 預期結果

- API 回傳 200，並取得 JWT Token
- UI 顯示登入頁面，輸入帳密後成功登入並跳轉

## 實際結果

API 回傳 200，成功取得 JWT Token。UI 登入頁面正常顯示，輸入 admin@devpro.com.tw 帳密後點擊登入，成功跳轉至主頁面。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FA001_login_page.png | 登入頁面 | ✅ |
| 002 | screenshots/002_FA001_input_credentials.png | 輸入帳號密碼 | ✅ |
| 003 | screenshots/003_FA001_login_success.png | 登入成功 | ✅ |

## 狀態判定

- ✅ PASS — 截圖符合預期結果

## 備註

無
