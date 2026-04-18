# FA-005：AdminDomain 設定

## 測試資訊
| 欄位 | 內容 |
|------|------|
| 測試日期 | 2026-04-18 |
| 測試人員 | 龍哥 🐉 |
| 功能編號 | FA-005 |
| 功能名稱 | AdminDomain 設定 |
| 測試環境 | Ubuntu-Devpro（VM）|

## 功能說明
`appsettings.json` 新增 `AdminDomains` 設定，指定 domain 下所有使用者登入後自動取得 Admin 角色，不需逐一列在 `AdminEmails`。

## 測試案例

| 案例 | 帳號 | 情境 | 預期結果 |
|------|------|------|----------|
| AD-001 | admin@devpro.com.tw | AdminEmails 命中 | isAdmin=true, role=Admin |
| AD-002 | abc@devpro.com.tw | AdminDomains 命中（非 AdminEmails）| isAdmin=true, role=Admin |
| AD-003 | user@msn.com | AllowedDomains 但非 AdminDomains | isAdmin=false, role=User |
| AD-004 | johnny@sinopac.com | 不在 AllowedEmailDomains | HTTP 401 拒絕登入 |
| AD-005 | ABC@DEVPRO.COM.TW | AdminDomains 大小寫不分 | isAdmin=true, role=Admin |

## 測試步驟
1. 確認 `appsettings.json` 的 `AdminDomains` 包含 `devpro.com.tw`
2. 以各測試帳號呼叫 `POST /api/auth/login`
3. 驗證回傳的 `isAdmin` 欄位與 JWT token 內的 `role` claim

## 預期結果
- `@devpro.com.tw` 任意帳號 → isAdmin=true
- 其他 AllowedDomain 帳號 → isAdmin=false
- 不在 AllowedDomains → HTTP 401
- domain 比對 case-insensitive

## 實際結果
✅ PASS — 5/5 案例全過（2026-04-18 TestV12-AdminDomain-0418-R1）

## 截圖清單
（API 測試，無截圖）

## 狀態判定
- ✅ PASS

## 備註
腳本：`QA/p003_test_v12_admin_domain.py`
結果：`QA/TestV12-AdminDomain-0418-R1/results.json`
