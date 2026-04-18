# P003-FileManager-WASM 行動計畫

> 建立日期：2026-04-11
> 狀態：待執行

---

## 背景

v5 R2 測試（54 案例）結果 38 PASS / 16 FAIL，其中：
- 7 個租戶隔離安全漏洞
- 3 個輸入驗證缺失
- Source code 分析發現 Download endpoint 無路徑驗證（Critical）
- 詳細結果：`QA/TestV5-Full-0411-R2/test_summary.md`
- 完整測試計畫：`QA/P003-TestPlan-v3-Comprehensive.md`

---

## 執行計畫（3 階段）

### Phase 1：修復安全漏洞（先修 bug）

#### 1-1. Download endpoint 路徑驗證（Critical）
- 檔案：`src/Server/Controllers/FilesController.cs` 第 82-91 行
- 問題：`GET /api/files/download` 沒有呼叫 `IsPathAllowed()`，任何登入使用者可下載系統任意檔案
- 修法：加入 `GetRootPathForUser()` + `IsPathAllowed()` 檢查
- 額外：`File.ReadAllBytes()` 改為 streaming（FileStreamResult），避免大檔案 OOM

#### 1-2. 租戶隔離修正（Critical，7 個 FAIL）
- 檔案：`src/Server/Controllers/FilesController.cs`
- 問題：`GET /api/files`、`PATCH /rename`、`PATCH /move`、`DELETE /` 沒有根據 user domain 限制路徑
- 修法：所有端點加入 domain 範圍檢查邏輯：
  ```
  if (!IsAdmin()) {
      var userRoot = GetRootPathForUser();
      if (!resolvedPath.StartsWith(userRoot)) return Forbid();
  }
  ```
- 影響的端點：
  - `GET /api/files` — 瀏覽目錄
  - `POST /api/folders` — 建立資料夾
  - `DELETE /api/files` — 刪除
  - `PATCH /api/files/move` — 移動（source 和 destination 都要檢查）
  - `PATCH /api/files/rename` — 重新命名
  - `POST /api/files/search` — 搜尋結果要過濾

#### 1-3. 輸入驗證修正（High，3 個 FAIL）
- `POST /api/folders`：檢查 name 非空、不含 `../` 或路徑分隔符，重複名稱回傳 409
- `PATCH /api/files/rename`：檢查 newName 非空、不含 `../` 或路徑分隔符
- `FileService.cs` 的 `IsPathAllowed()`：加入 `Path.GetFullPath()` resolve 後再比對

### Phase 2：修完後重跑 v5 測試驗證

- 跑 `p003_test_v5_full.py`（54 案例）
- 目標：之前 16 個 FAIL 應全部變 PASS（或至少安全相關的 10 個）
- 如果還有 FAIL，繼續修到全過

### Phase 3：執行 v3 擴展測試（105 案例）

把 `P003-TestPlan-v3-Comprehensive.md` 中新增的 51 個案例寫成自動化腳本：
- S7：安全深度測試（14 案例）— URL 編碼穿越、null byte、雙副檔名、download 漏洞
- S8：邊界條件（12 案例）— 空目錄、特殊字元、malformed JSON
- S9：並發競態（6 案例）— 同時操作同一檔案
- S10：效能壓力（5 案例）— 大目錄、大檔案
- S11：UI 狀態（8 案例）— 對話框殘留、Token 過期
- S12：JWT 安全（6 案例）— Token 竄改、過期

---

## 檔案位置索引

| 檔案 | 用途 |
|------|------|
| `QA/P003-TestPlan-v2.md` | v5 測試計畫（6 Stage, 54 案例） |
| `QA/P003-TestPlan-v3-Comprehensive.md` | v3 完整測試計畫（105 案例） |
| `QA/P003-Action-Plan.md` | 本文件（執行計畫） |
| `QA/p003_test_v5_full.py` | v5 測試腳本 |
| `QA/TestV5-Full-0411-R2/` | v5 R2 測試結果（38/54 PASS） |
| `QA/TestV5-Full-0411-R2/test_summary.md` | v5 R2 測試總表 |
| `QA/TestV5-Full-0411-R2/test_result_v5.json` | v5 R2 測試 JSON |

---

## 需要修改的原始碼檔案

| 檔案 | 修改內容 |
|------|---------|
| `src/Server/Controllers/FilesController.cs` | 所有端點加 domain 路徑檢查 + download 加 path validation + streaming |
| `src/Server/Controllers/FoldersController.cs` | 加 domain 路徑檢查 + name 驗證 |
| `src/Server/Controllers/UploadController.cs` | 加覆蓋提示或拒絕 |
| `src/Server/Services/FileService.cs` | IsPathAllowed 強化、rename/create 輸入驗證 |
