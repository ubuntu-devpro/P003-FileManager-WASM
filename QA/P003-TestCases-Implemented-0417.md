# P003-FileManager-WASM 已實作測試案例與驗收標準

> 建立日期：2026-04-17
> 涵蓋：v5 基本功能 + 租戶隔離（S1~S6，54 案）／v7 安全深度 + JWT（S7, S12，20 案）／v8 租戶矩陣補強（S13，28 案）
> 合計：**102 案例**
> 最新執行結果：94 PASS ／ 3 FAIL ／ 4 KNOWN（見 §5）

---

## 1. 測試帳號與角色矩陣

| 帳號 | 角色 | Domain | 根路徑 | 可見範圍 |
|------|------|--------|--------|---------|
| admin@devpro.com.tw | Admin | devpro.com.tw | `/home/devpro/data` | 全部三個 domain 資料夾 |
| johnny@sinopac.com | User | sinopac.com | `/home/devpro/data/sinopac.com` | 僅 sinopac.com |
| user@others.com | User | others.com | `/home/devpro/data/others.com` | 僅 others.com |

---

## 2. Stage 總表

| Stage | 主題 | 案例數 | 腳本 | 最新結果 |
|-------|------|--------|------|---------|
| S1 | 認證與權限 | 10 | `p003_test_v5_full.py` | 10/10 PASS |
| S2 | 租戶隔離（基本） | 10 | 同上 | 10/10 PASS |
| S3 | Admin CRUD | 11 | 同上 | 11/11 PASS |
| S4 | User CRUD | 7 | 同上 | 7/7 PASS |
| S5 | 跨帳號交互可見性 | 4 | 同上 | 4/4 PASS |
| S6 | 負向測試（登入/輸入） | 12 | 同上 | 12/12 PASS |
| S7 | 安全深度測試 | 14 | `p003_test_v7_security.py` | 10 PASS / 1 FAIL / 3 KNOWN |
| S12 | JWT Token 安全 | 6 | 同上 | 5 PASS / 1 KNOWN |
| S13 | 租戶矩陣補強 | 28 | `p003_test_v8_tenant.py` | 25 PASS / 3 FAIL |
| **合計** | | **102** | | **94 / 3 / 4** |

---

## 3. Stage 1：認證與權限（10 案）

### FA-001 登入
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| FA001-A-Admin | admin 登入 | HTTP 200 + JWT token 含 `role=Admin, domain=devpro.com.tw` |
| FA001-B-Johnny | johnny 登入 | HTTP 200 + JWT token 含 `role=User, domain=sinopac.com` |
| FA001-C-User | user 登入 | HTTP 200 + JWT token 含 `role=User, domain=others.com` |

### FA-002 首頁可見範圍
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| FA002-A-Admin | admin 登入後首頁 | 截圖：看到 devpro.com.tw、sinopac.com、others.com 三個 domain 資料夾 |
| FA002-B-Johnny | johnny 登入後首頁 | 截圖：僅見 sinopac.com 內容，不得見其他 domain |
| FA002-C-User | user 登入後首頁 | 截圖：僅見 others.com 內容 |

### FA-003 登出
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| FA003 | 使用者登出 | UI 回登入頁 + `localStorage.fm_token` 被清除 |

### FA-004 Session 驗證
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| FA004-A | 有效 token 呼叫 `/api/files` | HTTP 200 |
| FA004-B | 無效 token 呼叫 API | HTTP 401 |
| FA004-C | 無 token 呼叫 API | HTTP 401 |

---

## 4. Stage 2：租戶隔離（10 案）

測試主體為 **johnny（一般使用者）**。

### MT-001 路徑穿越防護
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| MT001-A | `GET /api/files?path=/home/devpro/data` | HTTP 200 + clamp 到 sinopac.com（不得見其他 domain） |
| MT001-B | `GET /api/files?path=.../others.com` | HTTP 403 |
| MT001-C | `GET /api/files?path=.../sinopac.com/../others.com` | HTTP 403（resolve 後跨域） |
| MT001-D | `GET /api/files?path=/etc/passwd` | HTTP 403 |

### MT-002 跨租戶寫入防護
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| MT002-A | johnny 上傳到 others.com | HTTP 403 |
| MT002-B | johnny 在 others.com 建資料夾 | HTTP 403 |
| MT002-C | johnny 刪除 others.com 檔案 | HTTP 403 |
| MT002-D | johnny 搬檔到 others.com | HTTP 403 |

### MT-003 跨租戶下載/搜尋防護
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| MT003-A | johnny 下載 others.com 檔案 | HTTP 403 |
| MT003-B | johnny 搜尋不得返回 others.com 結果 | 回傳 list 中無跨域項目 |

---

## 5. Stage 3：Admin 功能完整 CRUD（11 案）

admin 身份對整個 `/home/devpro/data` 的功能正確性驗證。

| 編號 | 功能 | 驗收標準 |
|------|------|---------|
| FM001 | 瀏覽資料夾 | 列表 items 正確 + UI 顯示檔名/大小/日期 |
| FM002 | 新增資料夾 | HTTP 200 + 重新 GET 能看到新資料夾 + UI 顯示 |
| FM003 | 重新命名 | HTTP 200 + 舊名消失新名出現（API + UI） |
| FM004 | 搬移檔案 | HTTP 200 + 檔案在新路徑可見 |
| FM005 | 刪除 | HTTP 200 + 檔案從列表消失 |
| FM006 | 單檔上傳 | HTTP 200 + API re-query 能看到新檔 |
| FM007 | 多檔上傳 | 所有檔案皆成功 |
| FM008 | 拖曳上傳（元件檢查） | UI 拖曳區元素存在 |
| FM009 | 單檔下載 | HTTP 200 + response body 為檔案內容 |
| FM010 | 多檔下載 | 每個檔都能下載成功 |
| FM011 | 搜尋 | 關鍵字命中，結果正確 |

---

## 6. Stage 4：User 功能 CRUD（7 案）

以 johnny 身份在自家 sinopac.com 執行核心功能。

| 編號 | 功能 | 驗收標準 |
|------|------|---------|
| FM001-U | 瀏覽自家 domain | 正常顯示 sinopac.com 內容 |
| FM002-U | 建立資料夾 | HTTP 200 + 新資料夾出現 |
| FM003-U | 重新命名 | HTTP 200 |
| FM005-U | 刪除 | HTTP 200 |
| FM006-U | 上傳 | HTTP 200 + verified=True |
| FM009-U | 下載 | HTTP 200 + 內容正確 |
| FM011-U | 搜尋（限 domain 內） | 結果全部在 sinopac.com 範圍，無跨域 |

---

## 7. Stage 5：跨帳號交互可見性（4 案）

| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| CA001 | admin 在 root 建資料夾 X | johnny 登入後看不到 X |
| CA002 | admin 在 sinopac.com 建資料夾 Y | johnny 登入後能看到 Y |
| CA003 | johnny 上傳檔案 Z 到 sinopac.com | admin 登入後在 sinopac.com 看得到 Z |
| CA004 | johnny 上傳 Z | user@others.com 完全看不到 |

---

## 8. Stage 6：負向測試（12 案）

### NE-001 登入錯誤處理
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| NE001-A | 錯誤密碼 | HTTP 401，無 token |
| NE001-B | 不存在帳號 | HTTP 401 |
| NE001-C | 空白帳號/密碼 | HTTP 400 |
| NE001-D | SQL injection `' OR 1=1 --` | HTTP 401（無繞過） |
| NE001-A-UI | 錯誤密碼 UI 顯示 | 畫面顯示錯誤訊息 |

### NE-002 檔案操作輸入驗證
| 編號 | 測試動作 | 驗收標準 |
|------|---------|---------|
| NE002-A | 建立重複名稱資料夾 | HTTP 400/409 |
| NE002-B | 重新命名為空字串 | HTTP 400 |
| NE002-C | 重新命名含 `../` | HTTP 400 |
| NE002-D | 刪除不存在路徑 | HTTP 200 + 明確訊息（不崩潰） |
| NE002-E | 上傳 .exe | 被擋，不落盤 |
| NE002-F | 上傳 0 bytes 空檔 | HTTP 200 + 正確落盤 |
| NE002-G | 搜尋空字串 | HTTP 200 + 結果合理（不崩潰） |

---

## 9. Stage 7：安全深度測試（14 案）

### SEC-001~005 路徑穿越變體
| 編號 | 攻擊向量 | 驗收標準 |
|------|---------|---------|
| SEC-001 | URL 編碼 `%2e%2e%2f` | HTTP 403/400，response 不得含 `/etc/passwd` 內容 |
| SEC-002 | 雙重編碼 `%252e%252e` | 同上 |
| SEC-003 | 反斜線 `..\\` | 同上 |
| SEC-004 | Null byte `%00` | HTTP 400/403/404（**目前 FAIL：回 500**） |
| SEC-005 | 超長路徑（4096 chars） | HTTP 4xx，不 500/crash |

### SEC-006~010 檔名攻擊
| 編號 | 攻擊向量 | 驗收標準 |
|------|---------|---------|
| SEC-006 | 建資料夾 name=`../../tmp/hacked` | HTTP 400 |
| SEC-007 | 重命名 newName 含路徑分隔符 | HTTP 400 |
| SEC-008 | 上傳檔名含 null byte `test\x00.exe` | 無 `.exe` 檔落盤 |
| SEC-009 | 雙副檔名 `malware.exe.txt` | 正常落盤（`.txt` 為最終副檔名）且不執行 |
| SEC-010 | 覆蓋已存在檔案 | 應拒絕或提示（**KNOWN：目前無聲覆蓋**） |

### SEC-011~013 下載端點安全
| 編號 | 攻擊向量 | 驗收標準 |
|------|---------|---------|
| SEC-011 | johnny 下載 `/etc/passwd` | HTTP 403，body 不得含 `root:x:` |
| SEC-012 | johnny 下載 others.com 檔案 | HTTP 403，不洩漏檔案內容 |
| SEC-013 | 下載 symlink → `/etc/passwd` | HTTP 403（**KNOWN：目前 follow symlink 洩漏**） |

### SEC-014 CORS
| 編號 | 攻擊向量 | 驗收標準 |
|------|---------|---------|
| SEC-014 | 惡意 Origin header | response 不應 `Access-Control-Allow-Origin: *` 或 echo rogue origin（**KNOWN：目前 AllowAnyOrigin**） |

---

## 10. Stage 12：JWT Token 安全（6 案）

| 編號 | 攻擊向量 | 驗收標準 |
|------|---------|---------|
| JWT-001 | 竄改 payload 的 role 為 Admin（保留原簽章） | HTTP 401（簽章驗證失敗） |
| JWT-002 | exp 改為過去時間 | HTTP 401 |
| JWT-003 | 改 issuer 為 `attacker.example.com` | HTTP 401 |
| JWT-004 | 改 audience 為 `attacker-audience` | HTTP 401 |
| JWT-005 | 空字串 token | HTTP 401 |
| JWT-006 | 登出後用舊 token | HTTP 401（**KNOWN：目前仍 200，無 blacklist**） |

---

## 11. Stage 13：租戶隔離矩陣補強（28 案）

為補強 v5 的覆蓋缺口：加入 `user@others.com` 作攻擊者、跨所有 domain 方向、Tree API、Move 反向、Rename 跨域、domain-root 操作、path 規範化邊界、admin sanity。

### Group A：johnny → devpro.com.tw（admin domain）9 案
| 編號 | 操作 | 驗收標準 |
|------|------|---------|
| MTX-A01 | browse | HTTP 403，response 不含 admin domain 標記 |
| MTX-A02 | tree | HTTP 403 |
| MTX-A03 | create folder | HTTP 403 |
| MTX-A04 | rename file | HTTP 403 |
| MTX-A05 | move devpro→sinopac | HTTP 403 |
| MTX-A06 | delete file | HTTP 403 + 檔案實際仍在 |
| MTX-A07 | upload | HTTP 403 或 200 但 success=false；磁碟無新檔 |
| MTX-A08 | download | HTTP 403 + body 不洩漏檔案內容 |
| MTX-A09 | search | HTTP 403 或 200 且 results 不含 admin 檔 |

### Group B：user@others.com 攻擊其他 domain 9 案
| 編號 | 操作 | 驗收標準 |
|------|------|---------|
| MTX-B01 | browse root（clamp 測試） | HTTP 200 且 items 不含 `devpro.com.tw`/`sinopac.com` |
| MTX-B02 | browse sinopac.com | HTTP 403 |
| MTX-B03 | browse devpro.com.tw | HTTP 403 |
| MTX-B04 | tree sinopac.com | HTTP 403 |
| MTX-B05 | upload 到 sinopac.com | HTTP 403；磁碟無新檔 |
| MTX-B06 | delete sinopac.com 檔 | HTTP 403；檔案仍在 |
| MTX-B07 | rename sinopac.com 檔 | HTTP 403 |
| MTX-B08 | move others.com→sinopac.com（dest 跨域） | HTTP 403 |
| MTX-B09 | download sinopac.com 檔 | HTTP 403 + 不洩漏內容 |

### Group D：Move 反向與混合 source 2 案
| 編號 | 操作 | 驗收標準 |
|------|------|---------|
| MTX-D01 | johnny move others.com→sinopac.com（source 跨域） | HTTP 403 |
| MTX-D02 | johnny move `[own, foreign]` 混合 source | HTTP 403（整批拒絕） |

### Group E：Rename 跨域 1 案
| 編號 | 操作 | 驗收標準 |
|------|------|---------|
| MTX-E01 | johnny rename others.com 檔 | HTTP 403 |

### Group F：Domain-root 本身操作 3 案
| 編號 | 操作 | 驗收標準 |
|------|------|---------|
| MTX-F01 | johnny rename 自己的 `sinopac.com` 資料夾 | HTTP 400/403（不可變更 tenant 邊界）。**目前 FAIL：HTTP 200 成功改名** |
| MTX-F02 | johnny delete 自己的 `sinopac.com` 資料夾 | HTTP 400/403。**目前 FAIL：HTTP 200 連同所有檔案一起刪光** |
| MTX-F03 | johnny move 自己 domain 資料夾到 `/data` root | HTTP 403 |

### Group G：Path 規範化邊界 1 案
| 編號 | 操作 | 驗收標準 |
|------|------|---------|
| MTX-G01 | `path=sinopac.com/../others.com` | HTTP 403（`Path.GetFullPath` resolve 後跨域應擋） |

### Group H：Admin sanity 3 案
| 編號 | 操作 | 驗收標準 |
|------|------|---------|
| MTX-H01 | admin 瀏覽所有 3 個 domain | 全部 HTTP 200 |
| MTX-H02 | admin 下載 sinopac 檔 | HTTP 200 + 內容正確（**目前 FAIL：被 F02 測試污染導致 404**） |
| MTX-H03 | admin 跨域 move（sinopac→devpro） | HTTP 200 |

---

## 12. 結果彙總與待修缺陷（2026-04-17）

### 最新執行狀態

| 測試集 | Run ID | 案例 | PASS | FAIL | KNOWN |
|--------|--------|------|------|------|-------|
| v5 基本+租戶 | TestV5-Full-0417-R1 | 54 | 54 | 0 | 0 |
| v7 安全+JWT | TestV7-Security-JWT-0417-R1 | 20 | 15 | 1 | 4 |
| v8 租戶矩陣 | TestV8-Tenant-Matrix-0417-R1 | 28 | 25 | 3 | 0 |
| **合計** | | **102** | **94** | **4** | **4** |

### 待修真 bug（3 個，扣除 H02 測試污染）

| 編號 | 嚴重度 | 問題 | 根因 |
|------|--------|------|------|
| **MTX-F02** | Critical | user 可刪除自己 domain root 資料夾，連同所有檔案消失 | `IsWithinUserScope` 判定 `fullPath == userRoot` 為 true；需排除 domain root 自身 |
| **MTX-F01** | High | user 可重新命名自己 domain root 資料夾，破壞 tenant 邊界 | 同上 |
| **SEC-004** | Medium | Null-byte path 讓 server 回 500（unhandled exception） | Controller 層缺乏 null-byte 清洗，例外直接 propagate |

### KNOWN 限制（4 個，v3 §8 已列）

| 編號 | 問題 | 建議處理時機 |
|------|------|-------------|
| SEC-010 | Upload 無聲覆蓋同名檔 | 上線前 |
| SEC-013 | Download 會 follow symlink（可讀系統檔） | 上線前，實務上比標籤嚴重 |
| SEC-014 | CORS `AllowAnyOrigin`（CSRF 風險） | 上線前 |
| JWT-006 | 登出後 token 無 blacklist | 長期規劃（需要 Redis 或 token revocation store） |

### H02 測試污染修正建議

v8 腳本順序：F02 執行完（bug 刪光檔案）→ teardown 重建資料夾但 marker 已失 → H02 download 回 404。修正：把 Group F 移到最後，或在 F02 後重新 replant fixture。

---

## 13. 未涵蓋區（依龍哥指示，效能/邊界延後）

| Stage | 案例數 | 狀態 |
|-------|--------|------|
| S8 邊界條件與異常處理 | 12 | **延後** |
| S9 並發與競態條件 | 6 | **延後** |
| S10 效能與壓力測試 | 5 | **延後** |
| S11 UI 狀態與互動完整性 | 8 | **延後** |
| 合計 | 31 | 預期上線前完成 |

---

## 14. 附錄：腳本與結果檔案對照

| 腳本 | 涵蓋 | 最新結果目錄 |
|------|------|-------------|
| `QA/p003_test_v5_full.py` | S1~S6 | `QA/TestV5-Full-0417-R1/` |
| `QA/p003_test_v7_security.py` | S7, S12 | `QA/TestV7-Security-JWT-0417-R1/` |
| `QA/p003_test_v8_tenant.py` | S13 | `QA/TestV8-Tenant-Matrix-0417-R1/` |
| 測試計畫參考 | 整體規劃 | `QA/P003-TestPlan-v2.md`, `QA/P003-TestPlan-v3-Comprehensive.md` |
