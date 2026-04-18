# P003-FileManager-WASM 系統化測試計畫 v2

> 建立日期：2026-04-11
> 基於：design.md 系統架構 + Test0411-Round3 測試結果
> 目的：補強多帳號/多租戶測試、建立分段驗證機制

---

## 1. 測試帳號與角色矩陣

系統有 3 組帳號，分屬不同角色與 domain：

| 帳號 | 角色 | Domain | 根路徑 | 可見範圍 |
|------|------|--------|--------|---------|
| admin@devpro.com.tw | **Admin** | devpro.com.tw | `/home/devpro/data` | 全部（含所有 domain 資料夾） |
| johnny@sinopac.com | **User** | sinopac.com | `/home/devpro/data/sinopac.com` | 僅 sinopac.com |
| user@others.com | **User** | others.com | `/home/devpro/data/others.com` | 僅 others.com |

---

## 2. 測試分段架構（Stage-Gate）

採用分段介入模式，每段結束做一次 AI 檢查點，失敗即中斷：

```
Stage 1: 認證與權限    →  AI 檢查點 1
Stage 2: 租戶隔離驗證  →  AI 檢查點 2
Stage 3: 功能操作 (Admin)  →  AI 檢查點 3
Stage 4: 功能操作 (User)   →  AI 檢查點 4
Stage 5: 跨帳號交互驗證    →  AI 檢查點 5
Stage 6: 負向測試          →  AI 檢查點 6
```

---

## 3. Stage 1：認證與權限（3 帳號各自測試）

### FA-001: 登入（每帳號各測一次）

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| FA-001-A | admin 登入 | API: status 200 + JWT token 包含 role=Admin, domain=devpro.com.tw |
| FA-001-B | johnny 登入 | API: status 200 + JWT token 包含 role=User, domain=sinopac.com |
| FA-001-C | user 登入 | API: status 200 + JWT token 包含 role=User, domain=others.com |

**AI 驗證重點：** 解析 JWT payload，確認 claims 正確（不只是 200 就 PASS）

### FA-002: 多網域權限（登入後看到的畫面不同）

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| FA-002-A | admin 登入後的首頁 | 截圖：應看到 sinopac.com、others.com、devpro.com.tw 等所有 domain 資料夾 |
| FA-002-B | johnny 登入後的首頁 | 截圖：應只看到 sinopac.com 底下的內容，**不應看到** others.com 或根目錄其他資料夾 |
| FA-002-C | user 登入後的首頁 | 截圖：應只看到 others.com 底下的內容 |

**AI 驗證重點：** 比對三張截圖，確認 admin 看到的範圍 > johnny > user，且各自只看到自己的 domain

### FA-003: 登出

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| FA-003-A | admin 登出 | UI：回到登入頁 + localStorage 中 fm_token 被清除 |
| FA-003-B | johnny 登出 | 同上 |

### FA-004: Session 驗證

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| FA-004-A | 帶有效 token 呼叫 /api/auth/session | API: 200 + 回傳使用者資訊 |
| FA-004-B | 帶過期/無效 token 呼叫 /api/auth/session | API: 401 |
| FA-004-C | 不帶 token 呼叫 /api/files | API: 401 |

### AI 檢查點 1

```
輸入：3 組帳號的登入截圖、JWT payload、首頁截圖
問題：
  1. 三個帳號是否都能成功登入？
  2. JWT claims 中的 role 和 domain 是否正確對應？
  3. 三個帳號登入後看到的檔案列表是否不同？
  4. admin 看到的範圍是否最大？
判斷：任一帳號登入失敗 → 中斷後續測試
```

---

## 4. Stage 2：租戶隔離驗證（最關鍵的安全測試）

此段全程以 johnny（一般使用者）身份操作，驗證他**不能**越權存取。

### MT-001: 路徑穿越防護

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| MT-001-A | johnny 呼叫 GET /api/files?path=/home/devpro/data | API: 應被拒絕（403 或空結果），不能看到根目錄 |
| MT-001-B | johnny 呼叫 GET /api/files?path=/home/devpro/data/others.com | API: 應被拒絕，不能看到別人的 domain |
| MT-001-C | johnny 呼叫 GET /api/files?path=/home/devpro/data/sinopac.com/../others.com | API: 路徑穿越攻擊，應被擋 |
| MT-001-D | johnny 呼叫 GET /api/files?path=/etc/passwd | API: 系統路徑，應被擋 |

### MT-002: 跨租戶寫入防護

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| MT-002-A | johnny 上傳檔案到 /home/devpro/data/others.com/ | API: 應被拒絕 |
| MT-002-B | johnny 在 /home/devpro/data/others.com/ 建立資料夾 | API: 應被拒絕 |
| MT-002-C | johnny 刪除 /home/devpro/data/others.com/ 下的檔案 | API: 應被拒絕 |
| MT-002-D | johnny 移動檔案到 /home/devpro/data/others.com/ | API: 應被拒絕 |

### MT-003: 跨租戶下載防護

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| MT-003-A | johnny 下載 /home/devpro/data/others.com/ 下的檔案 | API: 應被拒絕 |
| MT-003-B | johnny 搜尋，結果不應包含 others.com 的檔案 | API: 搜尋結果只包含 sinopac.com 的內容 |

### AI 檢查點 2

```
輸入：所有 MT 案例的 API request/response
問題：
  1. 所有跨租戶存取是否都被正確拒絕？
  2. 路徑穿越攻擊是否被攔截？
  3. 有沒有任何 API 回傳了不屬於 johnny 的資料？
判斷：任何一個越權存取成功 → 嚴重安全漏洞，立即標記
```

---

## 5. Stage 3：功能操作 — Admin 視角

以 admin 帳號執行完整 CRUD，這段和現有測試類似但**加強驗證邏輯**：

### FM-001: 資料夾瀏覽

| 步驟 | 動作 | 傳統 Assertion | AI 驗證 |
|------|------|---------------|---------|
| 1 | GET /api/files?path=根目錄 | status 200 + items 陣列非空 | — |
| 2 | 截圖首頁 | table 元素存在 | AI 看截圖：列表有無正確顯示檔名、大小、日期 |
| 3 | 雙擊 devpro.com.tw | — | AI 比對前後截圖：breadcrumb 是否更新、列表內容是否改變 |

### FM-002: 新增資料夾

| 步驟 | 動作 | 傳統 Assertion | AI 驗證 |
|------|------|---------------|---------|
| 1 | 截圖（操作前列表） | — | — |
| 2 | 點新增 → 輸入名稱 → 確認 | 對話框出現 + 輸入框可填 | — |
| 3 | API: POST /api/folders | status 200/201 | — |
| 4 | 截圖（操作後列表） | — | AI 比對前後截圖：新資料夾是否出現在列表中 |
| 5 | API: GET /api/files 重新查詢 | response 中包含新資料夾名稱 | — |

### FM-003 ~ FM-011（同樣模式）

每個功能都套用：
1. **操作前截圖**
2. **執行操作**（UI + API）
3. **操作後截圖**
4. **API 交叉驗證**（re-query 確認狀態變化）
5. **AI 比對前後截圖**

### AI 檢查點 3

```
輸入：所有 FM 案例的前後截圖 + API response
問題：
  1. 新增的資料夾是否真的出現在列表？
  2. 重新命名後，舊名稱是否消失、新名稱是否出現？
  3. 刪除後，被刪項目是否從列表移除？
  4. 上傳後，檔案是否出現在列表？
  5. 搜尋結果是否與關鍵字相關？
```

---

## 6. Stage 4：功能操作 — User 視角（johnny）

**以 johnny 帳號重跑一次核心 CRUD**，驗證一般使用者的功能是否正常：

| 編號 | 測試動作 | 重點驗證 |
|------|---------|---------|
| FM-001-U | 瀏覽 sinopac.com 目錄 | 能正常瀏覽自己的 domain |
| FM-002-U | 在 sinopac.com 下新增資料夾 | 能正常建立 |
| FM-003-U | 重新命名 sinopac.com 下的項目 | 能正常命名 |
| FM-005-U | 刪除 sinopac.com 下的項目 | 能正常刪除 |
| FM-006-U | 上傳檔案到 sinopac.com | 能正常上傳 |
| FM-009-U | 下載 sinopac.com 下的檔案 | 能正常下載 |
| FM-011-U | 搜尋 sinopac.com 下的檔案 | 搜尋範圍限定在 sinopac.com |

### AI 檢查點 4

```
輸入：johnny 的操作截圖 + API response
問題：
  1. johnny 在自己的 domain 內能正常執行所有 CRUD 嗎？
  2. UI 上有沒有顯示不屬於 sinopac.com 的任何資料？
  3. 搜尋結果是否全部都在 sinopac.com 範圍內？
```

---

## 7. Stage 5：跨帳號交互驗證

測試多帳號之間的操作是否互不影響：

| 編號 | 測試動作 | 驗證方式 |
|------|---------|---------|
| CA-001 | admin 在根目錄建立資料夾 X | johnny 登入後看不到 X（X 在根目錄，不在 sinopac.com 下） |
| CA-002 | admin 在 sinopac.com 下建立資料夾 Y | johnny 登入後能看到 Y |
| CA-003 | johnny 上傳檔案 Z 到 sinopac.com | admin 登入後在 sinopac.com 下能看到 Z |
| CA-004 | johnny 上傳檔案 Z 到 sinopac.com | user@others.com 登入後看不到 Z |

### AI 檢查點 5

```
輸入：各帳號的檔案列表截圖
問題：
  1. admin 的操作對 johnny 的可見性是否符合預期？
  2. johnny 的操作對 admin 是否可見？
  3. johnny 和 user 之間是否完全隔離？
```

---

## 8. Stage 6：負向測試

### NE-001: 登入相關

| 編號 | 測試動作 | 預期結果 |
|------|---------|---------|
| NE-001-A | 錯誤密碼登入 | API: 401 + UI 顯示錯誤訊息 |
| NE-001-B | 不存在的帳號登入 | API: 401 + UI 顯示錯誤訊息 |
| NE-001-C | 空白帳號/密碼登入 | API: 400 或 401 |
| NE-001-D | SQL Injection: email 填 `' OR 1=1 --` | API: 401（不能登入成功） |

### NE-002: 檔案操作相關

| 編號 | 測試動作 | 預期結果 |
|------|---------|---------|
| NE-002-A | 建立重複名稱的資料夾 | 應報錯或拒絕 |
| NE-002-B | 重新命名為空字串 | 應拒絕 |
| NE-002-C | 重新命名包含特殊字元 `../hack` | 應拒絕（路徑穿越） |
| NE-002-D | 刪除不存在的檔案路徑 | 應回傳 404 |
| NE-002-E | 上傳被封鎖的副檔名 .exe | 應被攔截拒絕 |
| NE-002-F | 上傳空檔案（0 bytes） | 應成功或明確拒絕 |
| NE-002-G | 搜尋空字串 | 應回傳空結果或全部 |

### AI 檢查點 6

```
輸入：所有負向測試的 API response + UI 截圖
問題：
  1. 所有錯誤輸入是否都被正確拒絕？
  2. 錯誤訊息是否友善（不洩漏系統資訊）？
  3. SQL Injection 和路徑穿越是否被攔截？
```

---

## 9. 測試案例總數統計

| Stage | 案例數 | 說明 |
|-------|--------|------|
| Stage 1: 認證與權限 | 11 | 3 帳號登入 + 權限畫面 + 登出 + Session |
| Stage 2: 租戶隔離 | 10 | 路徑穿越 + 跨租戶寫入/下載 |
| Stage 3: Admin CRUD | 11 | 現有 FM-001~011 強化版 |
| Stage 4: User CRUD | 7 | johnny 在自己 domain 的操作 |
| Stage 5: 跨帳號交互 | 4 | admin/johnny/user 互相可見性 |
| Stage 6: 負向測試 | 11 | 錯誤輸入 + 安全攻擊 |
| **合計** | **54** | |

對比原本只有 **15 個案例**，現在擴展到 **54 個**，主要補強了：
- 多帳號獨立測試（原本只用 admin）
- 租戶隔離安全驗證（原本完全沒有）
- 跨帳號交互影響（原本完全沒有）
- 負向測試（原本完全沒有）

---

## 10. 驗證方式分配

```
54 個案例的驗證方式分佈：

傳統 Assertion（確定性判斷）
├── HTTP status code 檢查        → ~40 個案例
├── JSON 欄位存在性檢查           → ~20 個案例
├── DOM 元素存在性檢查            → ~15 個案例
└── localStorage 狀態檢查         →  2 個案例

AI 驗證（需要判斷力）
├── 截圖前後比對（狀態變化）       → ~10 個案例
├── 截圖內容判讀（列表內容正確性） → ~8 個案例
├── 多截圖交叉比對（權限差異）     → 3 個案例（FA-002 三帳號）
├── API response 語意驗證          → ~5 個案例（搜尋結果相關性等）
└── 錯誤訊息品質判斷              → ~5 個案例（負向測試）

AI 檢查點（分段門檻）             → 6 個
```
