# FA-002：多網域權限

## 測試資訊

| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-07 |
| 測試人員 | 龍叔（Claude） |
| 功能編號 | FA-002 |
| 功能名稱 | 多網域權限 |
| 測試環境 | Ubuntu-Devpro（VM） |

## 功能說明

系統支援多網域使用者登入，不同網域的帳號皆可正常登入並依權限存取資源。Admin 可看到所有網域資料，一般使用者僅能看到自己網域的資料夾。

## 測試步驟

1. API 測試：以 admin 帳號登入，確認回傳 200
2. API 測試：以 user1（johnny@sinopac.com）登入，確認回傳 200
3. UI 測試：以 admin 登入，確認可見所有網域資料夾
4. UI 測試：以 johnny 登入，確認僅可見 sinopac.com 資料夾

## 預期結果

- admin 帳號登入回傳 200，可見所有網域資料夾
- johnny 帳號登入回傳 200，僅可見 sinopac.com 資料夾
- 路徑限制正確（johnny 路徑為 /home/devpro/data/sinopac.com）

## 實際結果

admin 帳號及 johnny@sinopac.com 帳號皆成功登入（API 回傳 200）。admin 視角可見所有網域資料夾；johnny 視角僅顯示 sinopac.com 資料夾，路徑正確限制為 /home/devpro/data/sinopac.com。

## 截圖清單

| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_FA002_admin_view.png | 管理員視角（可見所有網域） | ✅ |
| 002 | screenshots/002_FA002_user_view.png | 一般使用者視角（僅見 sinopac.com） | ✅ |

## 狀態判定

- ✅ PASS — 多網域權限隔離正確

## 備註

無
