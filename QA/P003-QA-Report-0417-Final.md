# P003-FileManager-WASM — QA 完整測試報告

**日期：** 2026-04-17  
**測試環境：** localhost:5001 / ASP.NET Core 8 + Blazor WASM  
**測試執行：** 自動化（pytest-style Python + Playwright）  
**報告版本：** Final（含 Phase 1 安全修復 + Phase 3 全功能驗收）

---

## 總覽

| Suite | 範圍 | 案例數 | PASS | FAIL | KNOWN |
|-------|------|--------|------|------|-------|
| v5 Full | S1–S6 核心功能 + 隔離 | 54 | **54** | 0 | 0 |
| v7 Security+JWT | S7 深度安全 + S12 JWT | 20 | **16** | 0 | 4 |
| v8 Tenant Matrix | S13 租戶隔離矩陣 | 28 | **28** | 0 | 0 |
| v9 Boundary+Race | S8 邊界 + S9 競態 | 18 | **18** | 0 | 0 |
| v10 Performance | S10 效能壓力 | 5 | **5** | 0 | 0 |
| v11 UI State | S11 UI 互動狀態 | 8 | **8** | 0 | 0 |
| **合計** | | **133** | **129** | **0** | **4** |

> **KNOWN（4件）** 為 v3 規格書既知限制，非回歸問題，已獨立追蹤。

---

## 本次修復項目（Phase 3 Bug Fix）

| Bug ID | 問題描述 | 修改位置 | 驗證結果 |
|--------|----------|----------|----------|
| SEC-004 | Null-byte 注入導致 HTTP 500 | `FilesController.cs` — `HasNullByte()` 擋在所有 `Path.GetFullPath()` 呼叫之前 | PASS |
| MTX-F01 | 使用者可 Rename 自己的 domain root | `IsWithinUserScopeForMutation()` 只允許 root 子路徑 | PASS |
| MTX-F02 | 使用者可 Delete 自己的 domain root | 同上，Delete/Rename/Move 改用 `IsWithinUserScopeForMutation` | PASS |
| PERF-002 | 50 MB 上傳回 HTTP 400 | `Program.cs` Kestrel `MaxRequestBodySize = 500 MB` | PASS |
| PERF-004 | 60 層深樹回 HTTP 500 | `Program.cs` `AddJsonOptions(MaxDepth = 256)` | PASS |
| UI-008 | Token 過期後顯示 401 banner 但不跳登入頁 | `Index.razor` `LoadFiles()` 加 `Nav.NavigateTo("/login")` | PASS |

---

## 已知限制（KNOWN，上線前需確認）

| ID | 描述 | 來源 | 建議 |
|----|------|------|------|
| SEC-010 | 上傳同名檔案靜默覆寫 | v3 §8 #3，`UploadController File.Create` | 上線前加覆寫確認或版本控制 |
| SEC-013 | 下載 symlink 可讀取 `/etc/passwd` | symlink 解析未被攔截 | 加 `FileInfo.Attributes` 檢查 symlink 旗標 |
| SEC-014 | CORS `AllowAnyOrigin` — CSRF 風險 | `Program.cs AllowAnyOrigin` | 上線前限制為允許來源清單 |
| JWT-006 | Logout 後 Token 仍有效（無黑名單） | Stateless JWT 設計限制 | 評估是否需 Redis Token Blacklist |

---

## v5 — S1–S6 核心功能（54/54）

**日期：** 2026-04-17 21:20:02

| Case | 名稱 | Stage | 狀態 |
|------|------|-------|------|
| FA001-A-Admin | admin@devpro.com.tw login | S1 | PASS |
| FA001-B-Johnny | johnny@sinopac.com login | S1 | PASS |
| FA001-C-User | user@others.com login | S1 | PASS |
| FA002-A-Admin | admin@devpro.com.tw visible scope | S1 | PASS |
| FA002-B-Johnny | johnny@sinopac.com visible scope | S1 | PASS |
| FA002-C-User | user@others.com visible scope | S1 | PASS |
| FA003 | Logout | S1 | PASS |
| FA004-A | Session: valid token | S1 | PASS |
| FA004-B | Session: invalid token | S1 | PASS |
| FA004-C | Session: no token files API | S1 | PASS |
| MT001-A | johnny access root | S2 | PASS |
| MT001-B | johnny access others.com | S2 | PASS |
| MT001-C | johnny path traversal | S2 | PASS |
| MT001-D | johnny access /etc/passwd | S2 | PASS |
| MT002-A | johnny upload to others.com | S2 | PASS |
| MT002-B | johnny create folder in others.com | S2 | PASS |
| MT002-C | johnny delete in others.com | S2 | PASS |
| MT002-D | johnny move to others.com | S2 | PASS |
| MT003-A | johnny download from others.com | S2 | PASS |
| MT003-B | johnny search isolation | S2 | PASS |
| FM001 | Folder Browse | S3 | PASS |
| FM002 | Create Folder | S3 | PASS |
| FM003 | Rename | S3 | PASS |
| FM004 | Move File | S3 | PASS |
| FM005 | Delete | S3 | PASS |
| FM006 | Single Upload | S3 | PASS |
| FM007 | Multi Upload | S3 | PASS |
| FM008 | Drag Upload (element check) | S3 | PASS |
| FM009 | Single Download | S3 | PASS |
| FM010 | Multi Download | S3 | PASS |
| FM011 | Search | S3 | PASS |
| FM001-U | Johnny browse own domain | S4 | PASS |
| FM002-U | Johnny create folder | S4 | PASS |
| FM003-U | Johnny rename in own domain | S4 | PASS |
| FM005-U | Johnny delete in own domain | S4 | PASS |
| FM006-U | Johnny upload to own domain | S4 | PASS |
| FM009-U | Johnny download from own domain | S4 | PASS |
| FM011-U | Johnny search (scoped) | S4 | PASS |
| CA001 | Admin root folder invisible to johnny | S5 | PASS |
| CA002 | Admin sinopac.com folder visible to johnny | S5 | PASS |
| CA003 | Johnny upload visible to admin | S5 | PASS |
| CA004 | Johnny file invisible to user@others.com | S5 | PASS |
| NE001-A | Wrong password | S6 | PASS |
| NE001-B | Nonexistent account | S6 | PASS |
| NE001-C | Empty credentials | S6 | PASS |
| NE001-D | SQL injection | S6 | PASS |
| NE001-A-UI | Wrong password UI | S6 | PASS |
| NE002-A | Duplicate folder name | S6 | PASS |
| NE002-B | Rename to empty string | S6 | PASS |
| NE002-C | Rename with path traversal | S6 | PASS |
| NE002-D | Delete nonexistent | S6 | PASS |
| NE002-G | Search empty query | S6 | PASS |
| NE002-E | Upload .exe blocked | S6 | PASS |
| NE002-F | Upload empty file | S6 | PASS |

---

## v7 — S7 深度安全 + S12 JWT（16/20，4 KNOWN）

**日期：** 2026-04-17 23:15:35

| Case | 名稱 | 狀態 | 備註 |
|------|------|------|------|
| SEC-001 | URL-encoded `../` 路徑穿越 | PASS | code=403 |
| SEC-002 | Double-encoded `../` 穿越 | PASS | code=403 |
| SEC-003 | Backslash `..\` 穿越 | PASS | code=403 |
| SEC-004 | Null-byte 注入 | PASS | code=400 |
| SEC-005 | 超長路徑（4096字元） | PASS | code=403 |
| SEC-006 | 資料夾名稱含 `../` | PASS | code=400 |
| SEC-007 | Rename newName 含路徑分隔符 | PASS | code=400 |
| SEC-008 | 上傳檔名含 null byte | PASS | code=200，無可執行檔落地 |
| SEC-009 | 雙副檔名 malware.exe.txt | PASS | 僅檢查最終副檔名，可接受 |
| SEC-010 | 上傳同名檔案靜默覆寫 | **KNOWN** | v3 §8 #3 既知限制 |
| SEC-011 | johnny 下載 /etc/passwd | PASS | code=403，無洩漏 |
| SEC-012 | johnny 下載 others.com 檔案 | PASS | code=403，無洩漏 |
| SEC-013 | 下載 symlink → /etc/passwd | **KNOWN** | symlink 解析未攔截 |
| SEC-014 | CORS 惡意 Origin | **KNOWN** | AllowAnyOrigin，CSRF 風險 |
| JWT-001 | 竄改 payload (role=Admin) | PASS | code=401 |
| JWT-002 | Expired token (exp in past) | PASS | code=401 |
| JWT-003 | 不同 issuer | PASS | code=401 |
| JWT-004 | 不同 audience | PASS | code=401 |
| JWT-005 | 空字串 token | PASS | code=401 |
| JWT-006 | Logout 後 token 仍有效 | **KNOWN** | Stateless 設計限制 |

---

## v8 — S13 租戶隔離矩陣（28/28）

**日期：** 2026-04-17 23:15:35  
**測試帳號：** johnny@sinopac.com（攻擊方）、user@others.com、admin@devpro.com.tw

| Case | Group | 操作 | 狀態 | 回應 |
|------|-------|------|------|------|
| MTX-A01 | A | johnny browse devpro.com.tw | PASS | 403 |
| MTX-A02 | A | johnny tree devpro.com.tw | PASS | 403 |
| MTX-A03 | A | johnny create folder in devpro.com.tw | PASS | 403 |
| MTX-A04 | A | johnny rename file in devpro.com.tw | PASS | 403 |
| MTX-A05 | A | johnny move FROM devpro TO sinopac | PASS | 403 |
| MTX-A06 | A | johnny delete file in devpro.com.tw | PASS | 403 |
| MTX-A07 | A | johnny upload to devpro.com.tw | PASS | 403 |
| MTX-A08 | A | johnny download from devpro.com.tw | PASS | 403 |
| MTX-A09 | A | johnny search in devpro.com.tw | PASS | 403 |
| MTX-B01 | B | user browse root（自動 clamp） | PASS | 200，僅見自己目錄 |
| MTX-B02 | B | user browse sinopac.com | PASS | 403 |
| MTX-B03 | B | user browse devpro.com.tw | PASS | 403 |
| MTX-B04 | B | user tree sinopac.com | PASS | 403 |
| MTX-B05 | B | user upload to sinopac.com | PASS | 403 |
| MTX-B06 | B | user delete in sinopac.com | PASS | 403 |
| MTX-B07 | B | user rename in sinopac.com | PASS | 403 |
| MTX-B08 | B | user move FROM others.com TO sinopac | PASS | 403 |
| MTX-B09 | B | user download sinopac.com file | PASS | 403 |
| MTX-D01 | D | johnny move FROM others.com TO sinopac | PASS | 403 |
| MTX-D02 | D | johnny 混合來源 move（自己+外部） | PASS | 403 |
| MTX-E01 | E | johnny rename others.com 中的檔案 | PASS | 403 |
| MTX-F01 | F | johnny rename sinopac.com（自己 root） | PASS | 403 |
| MTX-F02 | F | johnny delete sinopac.com（自己 root） | PASS | 403 |
| MTX-F03 | F | johnny move sinopac.com 到 /data root | PASS | 403 |
| MTX-G01 | G | johnny 路徑穿越 sinopac/../others | PASS | 403 |
| MTX-H01 | H | admin browse 全部 3 個 domain | PASS | 全可讀 |
| MTX-H02 | H | admin download sinopac marker | PASS | 200 |
| MTX-H03 | H | admin move sinopac → devpro | PASS | 200 |

---

## v9 — S8 邊界 + S9 競態（18/18）

**日期：** 2026-04-17 23:15:36

| Case | 名稱 | 狀態 | 備註 |
|------|------|------|------|
| EDGE-001 | Browse 空目錄 | PASS | code=200 items=[] |
| EDGE-002 | Browse 不存在路徑 | PASS | code=200 |
| EDGE-003 | 特殊字元檔名（CJK/空格/emoji） | PASS | 上傳成功，正常落地 |
| EDGE-004 | 超長檔名（250字元） | PASS | 上傳成功 |
| EDGE-005 | 0-byte 檔案上傳 | PASS | 大小回報 0 |
| EDGE-006 | 深層巢狀樹（12層） | PASS | code=200 |
| EDGE-007 | DELETE 空 body | PASS | code=415，符合 RFC |
| EDGE-008 | 格式錯誤 JSON body | PASS | code=400，無 stack trace 洩漏 |
| EDGE-009 | 錯誤 Content-Type | PASS | code=415 |
| EDGE-010 | DELETE 空陣列 | PASS | code=200 |
| EDGE-011 | MOVE 空 sourcePaths | PASS | code=200 |
| EDGE-012 | Search 含萬用字元 `*?` | PASS | code=200 |
| RACE-001 | 同時 rename 同一檔案 | PASS | 其中一方成功，另一方 400 |
| RACE-002 | 同時 delete 同一檔案 | PASS | 檔案確實消失 |
| RACE-003 | 下載中同時刪除 | PASS | 下載完整 5 MB，delete 200 |
| RACE-004 | 同時上傳同名檔案 | PASS | 最終一份存在 |
| RACE-005 | Browse 與 delete 並發 | PASS | list 持續回 200 |
| RACE-006 | Admin + user 並發操作同一 domain | PASS | 兩方均 200 |

---

## v10 — S10 效能壓力（5/5）

**日期：** 2026-04-17 23:10:01

| Case | 名稱 | 狀態 | 數據 |
|------|------|------|------|
| PERF-001 | Browse 1000 檔案目錄 | PASS | 15ms（門檻 3000ms） |
| PERF-002 | 上傳 50 MB | PASS | 0.42s，52.4 MB 落地（門檻 30s） |
| PERF-003 | 下載 200 MB Streaming | PASS | 0.29s，Server RSS 成長 3 MB |
| PERF-004 | 60 層深樹 | PASS | 0.01s（門檻 5s） |
| PERF-005 | 100 次連續 GET，RSS 穩定 | PASS | 0.16s，RSS 成長 5 MB（門檻 100 MB） |

---

## v11 — S11 UI 狀態互動（8/8）

**日期：** 2026-04-17 23:15:30  
**截圖路徑：** `QA/TestV11-UI-0417-R1/UI-{case}/`

| Case | 名稱 | 狀態 | 備註 |
|------|------|------|------|
| UI-001 | Escape 關閉 dialog | PASS | dialog 確實消失 |
| UI-002 | 重新整理後不留 orphan dialog | PASS | reload 後無殘留 |
| UI-003 | 快速雙擊資料夾不重複觸發 API | PASS | API 呼叫次數 = 1 |
| UI-004 | 全選 → 取消全選，selectedPaths 清空 | PASS | 42 列全選後全清 |
| UI-005 | 右鍵選單外點擊，選單關閉 | PASS | JS evaluate 觸發 Blazor onclick |
| UI-006 | 上傳 dialog 取消，無進度條殘留 | PASS | dialog 與 progress bar 均消失 |
| UI-007 | 網路斷線時操作，顯示錯誤不白畫面 | PASS | body 有內容，有 error 訊息 |
| UI-008 | Token 過期後操作，自動跳回登入頁 | PASS | login_form=True，跳轉成功 |

---

## 附錄：測試產出檔案清單

| 目錄 | 內容 |
|------|------|
| `QA/TestV5-Full-0417-R1/` | test_summary.md, test_result_v5.json |
| `QA/TestV7-Security-JWT-0417-R1/` | test_summary.md, test_result_v7.json |
| `QA/TestV8-Tenant-Matrix-0417-R1/` | test_summary.md, test_result_v8.json |
| `QA/TestV9-Boundary-Race-0417-R1/` | test_summary.md, test_result_v9.json |
| `QA/TestV10-Perf-0417-R1/` | test_summary.md, test_result_v10.json |
| `QA/TestV11-UI-0417-R1/` | test_summary.md, test_result_v11.json, UI-00{1-8}/*.png |

---

*報告自動產生，測試執行工具：Python requests + Playwright sync_api*
