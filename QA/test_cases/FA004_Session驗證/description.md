# FA-004：Session 驗證

## 測試資訊
| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-06 |
| 測試人員 | 龍哥 🐉 |
| 功能編號 | FA-004 |
| 功能名稱 | Session 驗證 |
| 測試環境 | Ubuntu-Devpro（VM）|

## 功能說明
已登入的使用者刷新頁面，系統透過 localStorage 的 JWT Token 自動還原 session。

## 測試步驟
1. 以 admin 登入
2. 刷新頁面
3. 觀察是否自動還原登入狀態

## 預期結果
- 刷新頁面後自動還原登入狀態，無需重新登入

## 實際結果
✅ PASS — JWT Token 存在 localStorage，刷新頁面後自動還原 session

## 截圖清單
（無專屬截圖，依賴其他截圖間接驗證）

## 狀態判定
- ✅ PASS

## 備註
依賴 AuthService.CheckSessionAsync() 在 Index.razor OnInitializedAsync 中呼叫。
