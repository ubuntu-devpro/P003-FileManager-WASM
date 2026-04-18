# P003-FileManager-WASM 測試計畫 v4（模組化）

> 建立日期：2026-04-18
> 前版：v3-Comprehensive（2026-04-11，105 案例）
> 本版變更：模組化重構 + 加入 2026-04-18 實測新發現案例

---

## 模組總覽

| 模組 | 代碼 | 說明 | 案例數 |
|------|------|------|--------|
| 認證與會話 | **AUTH** | 登入/登出、OTP、JWT、session 恢復 | 14 |
| 租戶隔離 | **TENANT** | 跨帳號存取、domain root 保護、admin 權限 | 32 |
| 檔案操作 | **FILE** | 瀏覽、上傳、下載、搜尋、重新命名、移動、刪除 | 20 |
| 安全性 | **SEC** | 路徑穿越、CORS、symlink、filename injection | 14 |
| UI 狀態 | **UI** | Dialog、錯誤顯示、路徑揭露、token 過期 | 10 |
| 基礎設施 | **INFRA** | Directory 自動建立、外網存取、server 狀態 | 3 |
| 邊界條件 | **EDGE** | 空輸入、特殊字元、malformed request | 12 |
| 並發 | **RACE** | 同時操作同一資源 | 6 |
| 效能 | **PERF** | 大目錄、大檔案、連續呼叫 | 5 |
| **合計** | | | **116** |

---

## AUTH — 認證與會話（14）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| AUTH-001 | 正確帳號密碼登入 | 200 + JWT token | ✅ PASS (v5) |
| AUTH-002 | 錯誤密碼登入 | 401，不洩漏原因 | ✅ PASS (v5) |
| AUTH-003 | 不在允許 domain 的 Email | 401「不允許的 Email 網域」 | ✅ PASS (v5) |
| AUTH-004 | 空帳號或空密碼 | 400 | ✅ PASS (v5) |
| AUTH-005 | 登出後呼叫受保護 API | 401 | ✅ PASS (v5) |
| AUTH-006 | 重新整理後 session 恢復（localStorage token） | 自動登入，不跳回 login | ✅ PASS (v5) |
| AUTH-007 | OTP 發送：email 送出 | Server log 顯示 EmailService 發信成功 | ✅ PASS (2026-04-18) |
| AUTH-008 | OTP 驗證成功 → 跳轉主畫面 | 登入完成，顯示正確 domain 目錄 | ✅ PASS (2026-04-18) |
| AUTH-009 | OTP 5 次錯誤後作廢 | 第 6 次輸入回 401，需重新發送 | ⬜ 待測 |
| AUTH-010 | OTP 超過 10 分鐘過期 | 401「驗證碼錯誤或已過期」 | ⬜ 待測 |
| AUTH-011 | OTP 一次性使用（成功後再用同碼） | 401 | ⬜ 待測 |
| AUTH-012 | 60 秒冷卻期間「重新發送」按鈕 disabled | 按鈕不可點擊，顯示倒數 | ⬜ 待測 |
| AUTH-013 | JWT payload 竄改（role 改 Admin） | 401 | ✅ PASS (v7) |
| AUTH-014 | 不同 issuer/audience/過期 token | 401 | ✅ PASS (v7) |

---

## TENANT — 租戶隔離（32）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| TENANT-001 | johnny 瀏覽 devpro.com.tw | 403 | ✅ PASS (v8) |
| TENANT-002 | johnny tree devpro.com.tw | 403 | ✅ PASS (v8) |
| TENANT-003 | johnny 建立資料夾於 devpro.com.tw | 403 | ✅ PASS (v8) |
| TENANT-004 | johnny 重新命名 devpro.com.tw 檔案 | 403 | ✅ PASS (v8) |
| TENANT-005 | johnny 移動 FROM devpro TO sinopac | 403 | ✅ PASS (v8) |
| TENANT-006 | johnny 刪除 devpro.com.tw 檔案 | 403 | ✅ PASS (v8) |
| TENANT-007 | johnny 上傳到 devpro.com.tw | 403 | ✅ PASS (v8) |
| TENANT-008 | johnny 下載 devpro.com.tw 檔案 | 403 | ✅ PASS (v8) |
| TENANT-009 | johnny 搜尋 devpro.com.tw | 403 | ✅ PASS (v8) |
| TENANT-010 | user 瀏覽 root（被 clamp 到自己 domain） | 200，只看到自己的目錄 | ✅ PASS (v8) |
| TENANT-011 | user 瀏覽 sinopac.com | 403 | ✅ PASS (v8) |
| TENANT-012 | user 上傳/刪除/重新命名到 sinopac.com | 403 | ✅ PASS (v8) |
| TENANT-013 | user move FROM others.com TO sinopac.com（dest 跨域） | 403 | ✅ PASS (v8) |
| TENANT-014 | johnny move FROM others.com TO sinopac（source 跨域） | 403 | ✅ PASS (v8) |
| TENANT-015 | johnny rename sinopac.com（自己的 domain root） | 403（不能改 root） | ✅ PASS (v8) |
| TENANT-016 | johnny delete sinopac.com（domain root） | 403 | ✅ PASS (v8) |
| TENANT-017 | johnny move sinopac.com 到 /data root | 403 | ✅ PASS (v8) |
| TENANT-018 | johnny traversal sinopac/../others | 403 | ✅ PASS (v8) |
| TENANT-019 | admin 瀏覽所有 3 個 domain | 200 all | ✅ PASS (v8) |
| TENANT-020 | admin 下載 sinopac marker | 200 | ✅ PASS (v8) |
| TENANT-021 | admin move sinopac → devpro | 200 | ✅ PASS (v8) |
| TENANT-022 | johnny downloads others.com file | 403 | ✅ PASS (v7) |
| TENANT-023 ~ 032 | （保留給多 domain 擴充測試） | | ⬜ 待設計 |

---

## FILE — 檔案操作（20）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| FILE-001 | 瀏覽目錄，列出檔案 | 200 + 正確 FileItem 列表 | ✅ PASS (v5) |
| FILE-002 | 建立資料夾 | 200，目錄存在 | ✅ PASS (v5) |
| FILE-003 | 重新命名檔案 | 200，舊名不存在，新名存在 | ✅ PASS (v5) |
| FILE-004 | 移動檔案 | 200，來源不存在，目的地有檔案 | ✅ PASS (v5) |
| FILE-005 | 刪除單一檔案 | 200，檔案消失 | ✅ PASS (v5) |
| FILE-006 | 刪除多個檔案 | 200，全部消失 | ✅ PASS (v5) |
| FILE-007 | 上傳單一檔案 | 200，檔案存在，大小正確 | ✅ PASS (v5) |
| FILE-008 | 上傳多個檔案 | 200，全部存在 | ✅ PASS (v5) |
| FILE-009 | 下載檔案，內容正確 | 200，bytes 正確 | ✅ PASS (v5) |
| FILE-010 | 搜尋關鍵字，回傳符合檔案 | 200，結果正確 | ✅ PASS (v5) |
| FILE-011 | 搜尋無符合，回傳空列表 | 200，[] | ✅ PASS (v5) |
| FILE-012 | tree API 回傳目錄結構 | 200，含子目錄 | ✅ PASS (v5) |
| FILE-013 | 刪除非空資料夾 | 200，遞迴刪除 | ✅ PASS (v5) |
| FILE-014 | 移動資料夾（含子項） | 200，結構完整 | ✅ PASS (v5) |
| FILE-015 | 上傳覆蓋已存在檔案（無聲覆蓋） | 200，檔案被覆蓋（**KNOWN**：無確認提示） | ✅ KNOWN (v7) |
| FILE-016 | 下載 streaming（大檔不 OOM） | 200，完整 bytes，server RSS 不暴增 | ✅ PASS (v10) |
| FILE-017 | 瀏覽 1000 檔目錄，效能 < 3s | 200，elapsed < 3000ms | ✅ PASS (v10) |
| FILE-018 | 上傳 50MB+ 檔案 | 200，大小正確，不 timeout | ✅ PASS (v10) |
| FILE-019 | 搜尋含 wildcard `*?` | 200，不崩潰 | ✅ PASS (v9) |
| FILE-020 | Deep nested tree（12 層） | 200，不 timeout | ✅ PASS (v9) |
| FILE-021 | 前端下載按鈕實際觸發，取得正確檔案（非 401） | Playwright expect_download，bytes > 0（**G-001**） | ✅ PASS (2026-04-18) |

---

## SEC — 安全性（14）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| SEC-001 | URL 編碼路徑穿越 `%2e%2e%2f` | 403/400 | ✅ PASS (v7) |
| SEC-002 | 雙重編碼 `%252e%252e` | 403/400 | ✅ PASS (v7) |
| SEC-003 | 反斜線穿越 `..\` | 403/400 | ✅ PASS (v7) |
| SEC-004 | Null byte 注入 `%00` | 400/403/404 | ✅ PASS (v7) |
| SEC-005 | 超長路徑（4096 chars） | 403 | ✅ PASS (v7) |
| SEC-006 | 建立資料夾名含 `../` | 400 | ✅ PASS (v7) |
| SEC-007 | rename newName 含路徑分隔符 | 400 | ✅ PASS (v7) |
| SEC-008 | 上傳檔名含 null byte | 200，但不落地 .exe | ✅ PASS (v7) |
| SEC-009 | 雙副檔名 malware.exe.txt | 200，只看最終副檔名（可接受） | ✅ PASS (v7) |
| SEC-010 | 上傳覆蓋已存在（無聲） | **KNOWN**（v3 §8 #3） | ✅ KNOWN (v7) |
| SEC-011 | johnny 下載 /etc/passwd | 403 | ✅ PASS (v7) |
| SEC-012 | johnny 下載 others.com 檔案 | 403 | ✅ PASS (v7) |
| SEC-013 | 下載 symlink → /etc/passwd | **KNOWN**（symlink 未攔截） | ✅ KNOWN (v7) |
| SEC-014 | CORS rogue Origin | **KNOWN**（AllowAnyOrigin） | ✅ KNOWN (v7) |

---

## UI — UI 狀態（10）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| UI-001 | Escape 關閉 dialog | dialog 關閉 | ✅ PASS (v11) |
| UI-002 | 重整後不留 orphan dialog | orphan = false | ✅ PASS (v11) |
| UI-003 | 快速雙擊不重複觸發 API | api_calls = 1 | ✅ PASS (v11) |
| UI-004 | 全選 → 取消全選，selectedPaths 清空 | count = 0 | ✅ PASS (v11) |
| UI-005 | 右鍵選單外點擊關閉 | menu closed | ✅ PASS (v11) |
| UI-006 | 上傳 dialog 取消無殘留 | dialog + progress gone | ✅ PASS (v11) |
| UI-007 | 網路斷線不白畫面 | 顯示錯誤訊息 | ✅ PASS (v11) |
| UI-008 | Token 過期跳登入頁 | redirect to /login | ✅ PASS (v11) |
| UI-009 | Breadcrumb 不揭露 server 路徑 | 顯示相對路徑，不含 `/home/devpro/data` | ✅ PASS (2026-04-18) |
| UI-010 | Move dialog 目標路徑不揭露 server 路徑 | 同上 | ✅ PASS (2026-04-18) |

---

## INFRA — 基礎設施（3）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| INFRA-001 | 新 domain 用戶第一次登入，tenant 目錄不存在 | 自動建立，不顯示「目錄不存在」 | ✅ PASS (2026-04-18) |
| INFRA-002 | 從外網（非 localhost）透過 Tailscale 存取 | API BaseAddress 動態跟隨 host，正常運作 | ✅ PASS (2026-04-18) |
| INFRA-003 | Server 重啟後，已登入 session 是否可用 | JWT 仍有效（stateless），OTP 記憶體清除需重新申請 | ⬜ 待測 |
| INFRA-004 | 行動裝置上傳檔案選擇器可選文件（非僅照片） | 不限 accept，可選任意檔案類型 | ✅ PASS (2026-04-18) |

---

## EDGE — 邊界條件（12）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| EDGE-001 | 瀏覽空資料夾 | 200 + [] | ✅ PASS (v9) |
| EDGE-002 | 瀏覽不存在路徑 | 200（clamp 到 root） | ✅ PASS (v9) |
| EDGE-003 | 檔名含特殊字元（中文/空白/emoji） | 上傳成功，正常顯示 | ✅ PASS (v9) |
| EDGE-004 | 非常長的檔名（250 chars） | 成功或明確拒絕 | ✅ PASS (v9) |
| EDGE-005 | 0-byte 檔案上傳 | 200，size = 0 | ✅ PASS (v9) |
| EDGE-006 | Deep nested 12 層目錄 | 200，不 timeout | ✅ PASS (v9) |
| EDGE-007 | DELETE 空 body | 400/415 | ✅ PASS (v9) |
| EDGE-008 | Malformed JSON body | 400，不洩漏 stack | ✅ PASS (v9) |
| EDGE-009 | 錯誤 Content-Type | 415 | ✅ PASS (v9) |
| EDGE-010 | DELETE paths 空陣列 | 200（無操作） | ✅ PASS (v9) |
| EDGE-011 | MOVE sourcePaths 空陣列 | 200（無操作） | ✅ PASS (v9) |
| EDGE-012 | 搜尋含 wildcard `*?` | 200，不崩潰 | ✅ PASS (v9) |

---

## RACE — 並發競態（6）

| 編號 | 案例 | 預期行為 | 狀態 |
|------|------|---------|------|
| RACE-001 | 同時 rename 同一檔案 | 一成功一失敗，不損毀 | ✅ PASS (v9) |
| RACE-002 | 同時 delete 同一檔案 | 一成功，檔案消失 | ✅ PASS (v9) |
| RACE-003 | 下載中刪除檔案 | 不崩潰 | ✅ PASS (v9) |
| RACE-004 | 同時上傳同名檔案 | 不產生損壞檔案 | ✅ PASS (v9) |
| RACE-005 | 瀏覽中刪除其中檔案 | 不崩潰 | ✅ PASS (v9) |
| RACE-006 | admin + user 同時操作同一 domain | 資料完整性 | ✅ PASS (v9) |

---

## PERF — 效能（5）

| 編號 | 案例 | 指標 | 狀態 |
|------|------|------|------|
| PERF-001 | 瀏覽 1000 檔目錄 | elapsed < 3000ms | ✅ PASS (v10) |
| PERF-002 | 上傳 50MB 檔案 | 不 OOM，elapsed < 30s | ✅ PASS (v10) |
| PERF-003 | 下載 200MB streaming | bytes 完整，RSS growth < 50MB | ✅ PASS (v10) |
| PERF-004 | Deep tree 60 層 | elapsed < 5s | ✅ PASS (v10) |
| PERF-005 | 100 次連續 GET | all 200，無記憶體洩漏 | ✅ PASS (v10) |

---

## 已知限制（KNOWN，不計入 FAIL）

| 編號 | 說明 | 追蹤 |
|------|------|------|
| KNOWN-001 | 上傳覆蓋同名檔案無警告（UploadController File.Create） | v3 §8 #3 |
| KNOWN-002 | Download symlink 未攔截（可讀系統檔） | v3 §8 #4 |
| KNOWN-003 | CORS AllowAnyOrigin（CSRF 風險） | 上線前修 |
| KNOWN-004 | JWT 無狀態，登出後舊 token 仍可用 | 設計限制 |
| KNOWN-005 | JWT secret key 硬編碼（上線前必改） | v3 §8 #6 |
| KNOWN-006 | 密碼明文比對，無 hash（上線前必改） | v3 §8 #7 |

---

## 統計

| 狀態 | 數量 |
|------|------|
| ✅ PASS | 97 |
| ✅ KNOWN（已知限制） | 6 |
| ⬜ 待測 | 13 |
| **合計** | **116** |

---

## 待測清單（優先序）

1. **AUTH-009~012**：OTP 完整流程（失敗鎖定、過期、一次性）
2. **INFRA-003**：Server 重啟後 session 狀態
3. **TENANT-023~032**：多 domain 擴充（msn.com 實際登入場景）
