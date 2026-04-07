好的，以下是我針對 **Test0407-Round5** 的完整分析與 QA 報告改進建議（只建議，不修改）：

---

## QA 報告改進建議 — Test0407-Round5 分析

### 一、已有建議文件的補充（P003-QA-Improvement-Suggestions.md 已涵蓋的部分）

現有建議文件已指出截圖數量不一致、description 模板、目錄結構等問題，**以下是額外發現或需要深化的建議**。

---

### 二、test_summary.md 與 test_result_v2.json 資料矛盾

**問題：**
- `test_summary.md:23` FM-004 備註寫「移動對話框**尚未實作**，僅顯示通知」
- `test_summary.md:28` FM-005 備註寫「**無確認對話框**，直接刪除」
- 但 `FM004_移動檔案/description.md` 實際結果明確記錄對話框已實作且正常運作（有 8 張截圖佐證）
- `FM005_刪除/` 在其他 Round 中也已修正加入確認對話框

**建議：** test_summary.md 的備註欄應與 description.md 的實際結果同步更新。目前 summary 保留了早期 Round 的舊備註，會誤導讀者。

---

### 三、Description.md 模板一致性問題

**問題：**
- FM-004 有「修正紀錄」區塊 → 良好範例
- FA-001、FM-008 **沒有**「修正紀錄」區塊
- FM-008 測試步驟僅 1 步（「UI 元件檢查」），過於簡略，未測試實際拖拉上傳流程

**建議：**
1. 所有 description.md 統一包含「修正紀錄」區塊（即使為空也寫「無」）
2. FM-008 的測試步驟應至少涵蓋：元件存在 → 模擬拖拉 → 確認上傳結果

---

### 四、FM-008 測試深度不足

**問題：**
- 僅驗證 Drop Zone 元素**存在**，未驗證拖拉上傳**功能**
- 只有 1 張截圖（`001_FM008_drag_upload.png`）
- test_result_v2.json 標記 `"api": true` 但實際 description 中無 API 測試步驟
- 這是 15 個案例中覆蓋率最低的

**建議：**
1. 補充 Playwright `page.dispatch_event` 模擬 drag-and-drop 操作
2. 至少 3 張截圖：Drop Zone 元件 → 拖拉中/檔案選取 → 上傳完成
3. 修正 JSON 中的 `api: true`，若未做 API 測試應標記 `false`

---

### 五、test_result_v2.json 準確性

**問題：**
- FA-004 標記 `"ui": true`，但 test_summary.md 和 description 都說「僅 API 驗證，無專屬 UI」
- FM-008 標記 `"api": true`，但 test_summary.md 標 `—`（未測 API）
- FM-010 同理，summary 標 API 為 `—`，JSON 卻為 `true`
- FA-003 也有類似問題

**建議：** JSON 結果檔應與 summary 表格、description.md 三方一致。可新增 JSON Schema 驗證或自動化檢查腳本。

---

### 六、缺少負向測試（Negative Test）

**問題：** 15 個案例全是正向路徑（Happy Path），沒有任何失敗場景的測試。

**建議新增：**

| 案例 | 負向測試 |
|------|---------|
| FA-001 | 錯誤密碼登入 → 應顯示錯誤訊息 |
| FA-004 | 過期/無效 Token → 應回傳 401 |
| FM-002 | 重複資料夾名稱 → 應拒絕建立 |
| FM-005 | 刪除不存在的檔案 → 應回傳 404 |
| FM-006 | 上傳超大檔案/禁止類型 → 應有錯誤提示 |
| FM-011 | 搜尋空字串/特殊字元 → 應正常處理 |

---

### 七、缺少跨 Round 的迴歸追蹤

**問題：**
- Round1~5 的演進僅在 summary 表格有通過率數字
- 沒有記錄「哪個案例在哪個 Round 失敗、為什麼失敗、怎麼修好的」
- `screenshots/dialogs_v5/` 目錄的歷史截圖用途不明

**建議：** 建立 `iteration_log.md`，格式如：

```
## Round 1 → Round 2 (66.7% → 80.0%)
- FM-002: FAIL → PASS，原因：wait_for_selector 改用 .rz-dialog
- FM-003: FAIL → PASS，原因：同上
- FM-009: FAIL → 仍 FAIL，原因：download event 尚未處理
```

---

### 八、DOCX 報告可強化項目

現有 DOCX 報告缺少：
1. **測試時間軸** — Round1~5 各自的執行時間（可從 JSON date 欄位取得）
2. **Bug 清單** — 即使已修復，也應列出發現過的問題（如 dialog 未出現、move 未實作等）
3. **環境版本資訊** — Blazor WASM 版本、.NET 版本、Playwright 版本
4. **API Response Time** — 可在自動化腳本中加入 response time 記錄

---

### 九、自動化改進建議

| 項目 | 現況 | 建議 |
|------|------|------|
| 資料一致性 | 手動維護三份資料（JSON/summary/description） | 寫腳本從 description.md 自動生成 JSON 與 summary |
| 截圖驗證 | 僅人眼檢查 | 可加 Playwright 的 `expect(page).to_have_screenshot()` 做視覺迴歸 |
| 報告生成 | 手動跑 `generate_docx_report.py` | 整合到測試腳本結尾自動產生 |

---

### 總結：優先順序

| 優先級 | 建議 | 理由 |
|--------|------|------|
| **高** | 修正 summary/JSON 資料矛盾 | 目前報告有錯誤資訊，影響可信度 |
| **高** | 補強 FM-008 測試深度 | 現有測試未驗證核心功能 |
| **高** | 新增負向測試案例 | 只有 Happy Path 無法保證系統穩健性 |
| **中** | 統一 description.md 模板 | FM-004 是好範例，其他案例應跟進 |
| **中** | 建立 iteration_log.md | 保留 Round1→5 的除錯知識 |
| **低** | 自動化資料一致性檢查 | 長期維護效率提升 |
| **低** | DOCX 報告補充環境/時間資訊 | 報告完整度提升 |
