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

使用者透過 Email 和密碼登入檔案管理器，系統驗證後回傳 JWT Token。

## 測試步驟

1. API：POST `/api/auth/login` 帶 `{ email, password }`
2. UI：開啟首頁，確認出現登入表單
3. UI：填入 admin@devpro.com.tw / admin123
4. UI：點擊「登入」按鈕
5. 確認登入成功，頁面跳轉至檔案列表

## 預期結果

- API 回傳 200 並含 JWT Token
- UI 顯示登入表單，填入後可成功登入

## 實際結果

API 回傳 200，成功取得 JWT Token。UI 登入表單正常顯示，填入帳密後成功登入並跳轉至檔案列表。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FA001_login_page.png | 登入頁面 | ✅ |
| 002 | screenshots/002_FA001_input_credentials.png | 填入帳密 | ✅ |
| 003 | screenshots/003_FA001_login_success.png | 登入成功 | ✅ |

## 狀態判定

✅ PASS — API 與 UI 均符合預期

## 備註

無
