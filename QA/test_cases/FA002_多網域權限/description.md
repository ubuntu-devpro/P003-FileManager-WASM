# FA-002：多網域權限

## 測試資訊
| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-06 |
| 測試人員 | 龍哥 🐉 |
| 功能編號 | FA-002 |
| 功能名稱 | 多網域權限 |
| 測試環境 | Ubuntu-Devpro（VM）|

## 功能說明
不同網域的帳號只能存取自己網域的檔案。Admin 可見全部，一般使用者只能見自己網域。

## 測試步驟
1. 以 johnny@sinopac.com 登入
2. 觀察首頁路徑是否為 /home/devpro/data/sinopac.com
3. 以 admin@devpro.com.tw 登入
4. 觀察首頁是否可見所有網域資料夾

## 預期結果
- johnny@sinopac.com 只能見 sinopac.com 下的檔案
- admin 可見所有網域

## 實際結果
✅ PASS — johnny 登入後路徑為 sinopac.com，admin 登入後可見所有資料夾

## 截圖清單
| 編號 | 截圖檔案 | 說明 | 狀態 |
|------|---------|------|------|
| 001 | screenshots/001_user_dashboard.png | johnny 儀表板（受限）| ✅ |
| 002 | screenshots/002_admin_dashboard.png | admin 儀表板（全域）| ✅ |

## 狀態判定
- ✅ PASS

## 備註
API 層已驗證：johnny 無法存取 devpro.com.tw 目錄（HTTP 403/目錄不存在）。
