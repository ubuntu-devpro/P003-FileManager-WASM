# P003-FileManager-WASM 變更紀錄

**用途：** 記錄開發過程中偏離原始規格的決定、踩到的坑、以及解決方案。

---

## 變更記錄

### [2026-04-06] v0.1 → v1.0（完整系統）

#### 🔴 重大偏離：從 Blazor Server 改為 Blazor WebAssembly

| 項目 | 原始決策（P002）| 變更後（P003）| 原因 |
|------|----------------|--------------|------|
| UI Framework | Blazor Server | Blazor WebAssembly | SignalR 電路在 headless 環境不穩定 |
| 即時通訊 | SignalR | 無（純 HTTP）| WASM 無需電路連線 |
| 認證方式 | Session Cookie | JWT Bearer Token | 無狀態，更適合 WASM |
| 自動化相容性 | ❌ 不穩定 | ✅ 穩定 | 原因同上 |

**影響範圍：** 整個前端架構重新設計

**驗證結果：** Playwright 截圖全部成功（18張），無電路中斷問題

---

#### 🔴 新增功能：登入系統（原本規格中沒有）

**發現情境：** QA 測試時發現 P003 沒有任何認證機制，任何人可直接存取檔案

**決定：** 緊急實作 JWT 登入系統

**實作內容：**
- JWT Bearer Token 認證
- `/api/auth/login` — 登入
- `/api/auth/session` — 驗證 session
- `/api/auth/logout` — 登出
- 預設帳號：admin@devpro.com.tw / johnny@sinopac.com

**文件更新：** 已補入功能需求規格書（FA-001 ~ FA-004）

---

#### 🔴 新增功能：多網域權限（原本規格中沒有）

**發現情境：** 討論時強哥提到需要區分不同 domain 帳號的存取權限

**決定：** 實作網域-based 檔案隔離

**實作內容：**
- Admin 可見 `/home/devpro/data/*`（全部網域）
- 一般使用者只看 `/home/devpro/data/{domain}/`
- API 層過濾，controller 從 JWT claims 取 domain

**文件更新：** 已補入功能需求規格書（第 4 節）

---

#### 🟡 UI 變更：從 Radzen Blazor Server 版改為 WASM 版

| 差異 | 說明 |
|------|------|
| Radzen 元件引用 | WASM 用 `_content/Radzen.Blazor/Radzen.Blazor.js` |
| Service 註冊 | `AddRadzenComponents()` 需在 Program.cs 呼叫 |
| Dialog Service | WASM 需正確初始化，否則 JS interop 報錯 |

**踩坑：** 初期 Radzen JS 未引用導致 `Error: Cannot read property 'dialog' of undefined`

**修復：** 在 `wwwroot/index.html` 加入 Radzen JS script

---

#### 🟡 QA 測試策略調整

**原訂策略：** 禮拜五 QA 流程（混合 API + Playwright）

**調整：** 由於 WASM 架構，優先確保 API 正常，再跑 UI 截圖

**結果：** API 全部通過，UI 截圖 18 張，覆蓋 FM-001~FM-011 + 登入流程

---

### [2026-04-05] 專案初始化

#### 決定：使用 Blazor WebAssembly（而非 Blazor Server）

**原因：**
1. P002（Blazor Server）已知有 SignalR 電路問題
2. WASM 架構更適合純 API + 自動化優先的場景
3. 無需維護伺服器端的 UI 狀態

**取捨：**
- 放棄：Blazor Server 的快速初始載入（需下載 WASM）
- 獲得：無電路問題、自動化穩定、簡單部署

---

## 已知問題

| 問題 | 嚴重度 | 說明 |
|------|--------|------|
| UI 底部 unhandled error | ⚠️ 低 | 不影響功能，截圖都可正常跑 |
| 無檔案分享連結 | 🟡 未實作 | 不在原始需求中 |
| 無回收筒 | 🟡 未實作 | 不在原始需求中 |
| 無使用者註冊 | ✅ 刻意不實作 | 內部系統，帳號由管理員分發 |

---

## 未來可擴充項目

- [ ] 將使用者移至資料庫（Entity Framework Core）
- [ ] 實作檔案分享連結
- [ ] 實作回收筒功能
- [ ] 支援多語系（i18n）
- [ ] 響應式設計（支援手機）

---

_本文件最後更新：2026-04-06 16:21 GMT+8_
_建立者：龍哥 🐉_
