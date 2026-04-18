# QA 測試通則規範

> 建立日期：2026-04-18
> 適用範圍：P003-FileManager-WASM 及後續同類 Blazor WASM + JWT API 專案

---

## 1. 測試層次原則

任何功能必須在**正確的測試層次**驗證，否則測試通過不代表使用者能正常使用。

| 層次 | 工具 | 測試對象 | 限制 |
|------|------|---------|------|
| L1 API 層 | curl / pytest requests | Server 邏輯、Auth、輸入驗證 | **不含瀏覽器行為** |
| L2 前端整合層 | Playwright / Selenium | 前端 → API 完整呼叫鏈 | 含 header、cookie、JS 行為 |
| L3 E2E 層 | Playwright（有帳號） | 真實使用者操作流程 | 最貼近實際，成本最高 |

**規則：凡涉及「前端如何呼叫 API」的功能，必須有 L2 或 L3 測試，L1 單獨通過不足以確認功能正常。**

---

## 2. 已知易犯盲點

### G-001：瀏覽器導航不帶 Authorization Header

**問題描述：**
瀏覽器原生導航行為（`window.open`、`<a href>`、`location.href`）不會自動附加 JWT Bearer token，導致受保護的 API endpoint 回傳 401，即使 L1 curl 測試完全通過。

**觸發場景：**
- 檔案下載（`/api/files/download`）
- 圖片/媒體預覽（直接 URL 存取）
- 任何用瀏覽器導航觸發的 GET endpoint

**正確驗證方式：**
- 必須用 Playwright `expect_download()` 實際觸發下載，確認檔案取得成功
- 不可只用 curl + token 測試 API 回傳 200 就算通過

**正確實作方式：**
- 用 `HttpClient.GetAsync()` 取回 bytes（自動帶 Auth header）
- 再透過 JS blob + `<a download>` 觸發瀏覽器儲存

**P003 本案對應：** FILE-021

---

### G-002：行動裝置 `accept` 屬性行為與桌面不同

**問題描述：**
`<input type="file" accept="*/*">` 在 iOS Safari / Android Chrome 行動瀏覽器上，可能被解讀為「僅開啟媒體選擇器」而非「開啟檔案管理員」，導致使用者只能選照片。

**正確驗證方式：**
- 上傳功能必須在**實際行動裝置或模擬器**測試，不能只在桌面瀏覽器驗證

**正確實作方式：**
- 不設定 `accept` 屬性，讓瀏覽器自行決定（顯示完整檔案選擇器）
- 若需限制類型，明確列出 MIME type，避免使用萬用符號

**P003 本案對應：** INFRA-004

---

### G-003：API 測試用的 Token 與前端實際取得的 Token 來源不同

**問題描述：**
L1 測試腳本通常手動登入取得 token 後直接帶入，但前端可能因 localStorage 過期、WASM 初始化順序等因素，實際拿不到有效 token。

**正確驗證方式：**
- Session 恢復、token 過期跳轉等行為，必須用 Playwright 模擬完整登入流程後再操作

**P003 本案對應：** AUTH-006、UI-008

---

### G-004：新租戶目錄不存在

**問題描述：**
系統以 domain 為單位建立使用者目錄，若 domain 第一次使用，對應目錄不存在，前端顯示錯誤。

**正確驗證方式：**
- 每次加入新 domain 帳號時，測試「第一次登入」的完整流程，確認目錄自動建立

**P003 本案對應：** INFRA-001

---

### G-005：Server 路徑不應揭露給前端使用者

**問題描述：**
前端 UI 直接顯示 API 回傳的 server 絕對路徑（如 `/home/devpro/data/msn.com`），揭露伺服器目錄結構，屬於資訊洩漏。

**正確驗證方式：**
- 所有路徑相關 UI（breadcrumb、dialog、錯誤訊息）都不應出現 server 根目錄的絕對路徑
- Playwright 測試應抓取 breadcrumb 文字，確認不含敏感前綴

**P003 本案對應：** UI-009、UI-010

---

## 3. 測試覆蓋度檢核表

每個功能模組上線前，確認以下項目：

| 檢核項目 | 必要層次 |
|---------|---------|
| API 認證保護（401/403） | L1 |
| 輸入驗證（400） | L1 |
| 租戶隔離（403） | L1 |
| **前端觸發下載** | **L2 Playwright** |
| **前端表單送出（含 token）** | **L2 Playwright** |
| **行動裝置互動（上傳、選擇器）** | **L3 實機 or 模擬器** |
| **路徑/敏感資訊不外露** | **L2 Playwright** |
| 新帳號/新 domain 首次使用 | L3 |

---

## 4. 版本紀錄

| 版本 | 日期 | 異動 |
|------|------|------|
| v1.0 | 2026-04-18 | 初版建立，含 G-001~G-005 |
