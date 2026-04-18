# P003-FileManager-WASM 嚴謹測試計畫 v3

> 建立日期：2026-04-11
> 基於：v5 R2 測試結果 (38/54 PASS) + 原始碼逐行分析
> 目的：補齊所有遺漏的測試維度

---

## 1. 現有覆蓋 vs 缺口總覽

### 已覆蓋（v5 的 54 個案例）

| 維度 | 覆蓋狀態 |
|------|---------|
| 認證登入/登出 | 已覆蓋 |
| 多帳號基本 CRUD | 已覆蓋 |
| 租戶隔離（API 層） | 已覆蓋，**發現 7 個漏洞** |
| 負向測試（登入失敗） | 已覆蓋 |
| 負向測試（輸入驗證） | 部分覆蓋 |

### 尚未覆蓋（本文補強）

| 維度 | 案例數 | 嚴重度 |
|------|--------|--------|
| **S7: 安全性深度測試** | 14 | Critical |
| **S8: 邊界條件與異常處理** | 12 | High |
| **S9: 並發與競態條件** | 6 | High |
| **S10: 效能與壓力測試** | 5 | Medium |
| **S11: UI 狀態與互動完整性** | 8 | Medium |
| **S12: JWT Token 安全測試** | 6 | High |
| 合計新增 | **51** | |
| 加上 v5 原有 | **105 總計** | |

---

## 2. S7: 安全性深度測試（14 案例）

### 路徑穿越攻擊（擴展）

目前 v5 只測了基本的 `../`，但後端有多個繞過可能：

| 編號 | 攻擊向量 | 測試方式 |
|------|---------|---------|
| SEC-001 | URL 編碼穿越 `%2e%2e%2f` | GET /api/files?path=%2e%2e%2fetc |
| SEC-002 | 雙重編碼 `%252e%252e` | GET /api/files?path=%252e%252e |
| SEC-003 | 反斜線穿越 `..\\` | GET /api/files?path=..\\etc |
| SEC-004 | Null byte 注入 `%00` | GET /api/files?path=/home/devpro/data%00/etc/passwd |
| SEC-005 | 超長路徑 (4096+ chars) | GET /api/files?path=AAAA...（4096 個 A） |

### 檔案名稱攻擊

| 編號 | 攻擊向量 | 測試方式 |
|------|---------|---------|
| SEC-006 | 建立資料夾名含 `../` | POST /api/folders?name=../../../tmp/hacked |
| SEC-007 | 重新命名含路徑分隔符 | PATCH /api/files/rename newName="../../etc/shadow" |
| SEC-008 | 上傳檔名含 null byte | 上傳 test%00.exe → 繞過副檔名檢查 |
| SEC-009 | 雙副檔名繞過 | 上傳 malware.exe.txt → 是否被擋 |
| SEC-010 | 上傳覆蓋已存在檔案 | 上傳同名檔案，驗證是否無聲覆蓋 |

### 下載端點安全（FilesController.Download 無路徑檢查！）

| 編號 | 攻擊向量 | 測試方式 |
|------|---------|---------|
| SEC-011 | johnny 下載 /etc/passwd | GET /api/files/download?path=/etc/passwd (johnny token) |
| SEC-012 | johnny 下載 others.com 檔案 | GET /api/files/download?path=/home/devpro/data/others.com/test.txt |
| SEC-013 | 下載 symlink 指向系統檔 | 建立 symlink → 透過 API 下載 |

### CORS 攻擊

| 編號 | 測試方式 |
|------|---------|
| SEC-014 | 從不同 origin 發送 API request，驗證 CORS 是否允許（目前 AllowAnyOrigin = 有 CSRF 風險） |

---

## 3. S8: 邊界條件與異常處理（12 案例）

### 檔案系統邊界

| 編號 | 情境 | 預期行為 |
|------|------|---------|
| EDGE-001 | 瀏覽空資料夾 | 回傳空列表，UI 顯示「無檔案」 |
| EDGE-002 | 瀏覽不存在的路徑 | 回傳錯誤，不是 500 |
| EDGE-003 | 檔名含特殊字元（中文、空白、emoji） | 正常顯示與操作 |
| EDGE-004 | 非常長的檔名（255 chars） | 正常處理或明確拒絕 |
| EDGE-005 | 檔案大小為 0 bytes | 正確顯示大小，可下載 |
| EDGE-006 | 深層巢狀目錄（10+ 層） | tree API 和 UI 都能正常顯示 |

### API 請求邊界

| 編號 | 情境 | 預期行為 |
|------|------|---------|
| EDGE-007 | 空 request body | 400 Bad Request，不是 500 |
| EDGE-008 | JSON 格式錯誤 | 400，不洩漏堆疊資訊 |
| EDGE-009 | Content-Type 錯誤 | 415 Unsupported Media Type |
| EDGE-010 | DELETE 空陣列 `{"paths":[]}` | 明確回應，不是 200 |
| EDGE-011 | MOVE 空來源 `{"sourcePaths":[]}` | 明確回應 |
| EDGE-012 | 搜尋含 wildcard 字元 `*?` | 正常處理不崩潰 |

---

## 4. S9: 並發與競態條件（6 案例）

| 編號 | 情境 | 測試方式 | 預期行為 |
|------|------|---------|---------|
| RACE-001 | 同時重新命名同一檔案 | 2 個並發 PATCH /rename | 一個成功一個失敗，不資料損毀 |
| RACE-002 | 同時刪除同一檔案 | 2 個並發 DELETE | 一個成功一個 404 |
| RACE-003 | 刪除正在下載的檔案 | 先發 GET /download，同時發 DELETE | 不崩潰 |
| RACE-004 | 上傳同名檔案同時進行 | 2 個並發 POST /upload | 不產生損壞檔案 |
| RACE-005 | 瀏覽目錄同時刪除其中檔案 | GET /files + DELETE 並發 | 不崩潰 |
| RACE-006 | 2 個帳號同時操作同一 domain | admin + johnny 同時改 sinopac.com | 資料完整性 |

---

## 5. S10: 效能與壓力測試（5 案例）

| 編號 | 情境 | 量化指標 |
|------|------|---------|
| PERF-001 | 瀏覽含 1000 個檔案的目錄 | 回應時間 < 3 秒 |
| PERF-002 | 上傳 100MB 檔案 | 不 OOM，有進度回報 |
| PERF-003 | 下載大檔案（500MB+） | 後端用 ReadAllBytes 會 OOM → **已知問題** |
| PERF-004 | 深層目錄 tree API（100+ 資料夾） | 不 timeout |
| PERF-005 | 連續 100 次 API 呼叫 | 無記憶體洩漏、無 rate limit crash |

---

## 6. S11: UI 狀態與互動完整性（8 案例）

| 編號 | 情境 | 驗證方式 |
|------|------|---------|
| UI-001 | 對話框開啟中按 Escape | 對話框關閉，不殘留 |
| UI-002 | 對話框開啟中切換頁面 | 不產生 orphan dialog |
| UI-003 | 快速雙擊資料夾（防重複觸發） | 不發 2 次 API 請求 |
| UI-004 | 全選 checkbox → 取消全選 | selectedPaths 正確清空 |
| UI-005 | 右鍵選單 → 點擊選單外區域 | 選單關閉 |
| UI-006 | 上傳進度條中途取消 | 不殘留進度條 |
| UI-007 | 網路斷線時操作 | 顯示錯誤訊息，不白畫面 |
| UI-008 | Token 過期後操作 | 自動跳回登入頁 |

---

## 7. S12: JWT Token 安全測試（6 案例）

| 編號 | 情境 | 預期行為 |
|------|------|---------|
| JWT-001 | 竄改 token payload（改 role 為 Admin） | 401（簽名驗證失敗） |
| JWT-002 | 過期 token 存取 API | 401 |
| JWT-003 | 不同 issuer 的 token | 401 |
| JWT-004 | 不同 audience 的 token | 401 |
| JWT-005 | 空字串 token | 401 |
| JWT-006 | 登出後用舊 token 存取 API | 200（JWT 無狀態，**已知限制**） |

---

## 8. 原始碼層級發現的 Critical Bug（非測試範圍，但必須修）

這些是讀 source code 時發現的，不是靠測試找到的：

| # | 檔案:行號 | 問題 | 嚴重度 |
|---|-----------|------|--------|
| 1 | `FilesController.cs:82-91` | **Download endpoint 沒有 path validation**，任何登入使用者都可以下載系統任意檔案（`/etc/passwd`） | **Critical** |
| 2 | `FilesController.cs:88` | `File.ReadAllBytes()` 讀取整個檔案到記憶體，大檔案會 OOM crash server | **High** |
| 3 | `UploadController.cs:41` | `File.Create()` 會**無聲覆蓋**同名檔案，沒有任何提示 | **High** |
| 4 | `FileService.cs:87-102` | `BuildTree()` 遞迴沒有深度限制，circular symlink 會 stack overflow | **Medium** |
| 5 | `FileService.cs:190` | Delete 的計數器對不存在的路徑也 +1，回傳的 deleted count 不準 | **Low** |
| 6 | `JwtService.cs:17` | JWT secret key 硬編碼在程式碼中 | **Critical**（上線前） |
| 7 | `JwtService.cs:33` | 密碼明文比對，無 hash | **Critical**（上線前） |
| 8 | `Program.cs:37-40` | CORS AllowAnyOrigin，允許 CSRF 攻擊 | **High**（上線前） |

---

## 9. 建議的測試優先順序

```
第一優先：修 bug 而非測試
  ├── Download endpoint 路徑驗證（SEC-011 會直接證實）
  ├── 租戶隔離修正（v5 已發現的 7 個 FAIL）
  └── 輸入驗證（NE002-A/B/C）

第二優先：安全性測試 S7（14 案例）
  ├── 路徑穿越變體（SEC-001~005）
  ├── 檔案名稱攻擊（SEC-006~010）
  └── 下載端點安全（SEC-011~013）

第三優先：JWT 安全 S12（6 案例）
  └── Token 竄改、過期、跨 issuer

第四優先：邊界條件 S8 + 並發 S9（18 案例）
  └── 空輸入、特殊字元、race condition

第五優先：效能 S10 + UI S11（13 案例）
  └── 大檔案、高併發、UI 狀態
```

---

## 10. 測試總量

| 版本 | 案例數 | 涵蓋範圍 |
|------|--------|---------|
| v4（原始） | 15 | 基本功能 smoke test |
| v5（今天） | 54 | + 多帳號、租戶隔離、負向測試 |
| **v3 計畫（本文）** | **105** | + 安全深度、邊界條件、並發、效能、JWT |
