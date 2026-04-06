# P003 WASM 截圖環境問題

## 標題
Kestrel 服務 Blazor WASM 時 `.dat` 檔案 404 — 截圖環境修復實錄

## Tags
`#Blazor-WASM` `#Kestrel` `#MIME-type` `#CORS` `#QA環境` `#Playwright` `#dotnet8`

---

## 症狀

用 Playwright 截圖時，應用程式一直停留在登入頁（`/login`），WASM 初始化失敗，頁面按鈕只有 1 個（登入按鈕），無法看到檔案列表。

## 根本原因

**原因 A — CORS 設定不完整**
- `Program.cs` 的 CORS policy 只允許 `localhost:5000` 和 `localhost:5001`
- 使用 Python HTTP server (`localhost:5002`) 被 CORS 擋住

**原因 B — Kestrel 不認 `.dat` 副檔名**
- WASM 需要的 ICU data 檔案（`icudt_EFIGS.dat`）是 `.dat` 副檔名
- Kestrel 預設的 MIME type mapping 沒有 `.dat`，回傳 404
- 導致 Blazor WASM 無法正常初始化

**原因 C — localStorage key 用錯**
- 注入的 JWT token key 是 `auth_token`
- 但程式碼實際用的是 `fm_token`
- 導致即使手動注入 token 也無法通過 client-side auth

## 解決方案

**修復 1 — CORS + MIME type（`Program.cs`）**
```csharp
// CORS 加入 localhost:5002
policy.WithOrigins("http://localhost:5000", "http://localhost:5001", "http://localhost:5002")

// MIME type 加入 .dat
provider.Mappings[".dat"] = "application/octet-stream";
provider.Mappings[".dll"] = "application/octet-stream";
provider.Mappings[".wasm"] = "application/wasm";
// 並啟用 ServeUnknownFileTypes
```

**修復 2 — 用對的 JWT key（`fm_token`）**
```javascript
localStorage.setItem('fm_token', '<JWT_TOKEN>');
```

**修復 3 — 統一用 dotnet server（`localhost:5001`）**
- 放棄 Python HTTP server
- dotnet server 修好 MIME 後就能完整服務 WASM static files

## 關鍵判斷技巧

| 訊號 | 代表的問題 |
|------|----------|
| 按鈕只有 1 個（登入）| WASM 未初始化或 auth 失敗 |
| `_framework/icudt_*.dat` 回傳 404| Kestrel MIME type 設定問題 |
| `localStorage.getItem('fm_token')` 是 null| key 用錯，應該是 `fm_token` 不是 `auth_token` |
| Python server 能送出 `.dat` 但 dotnet server 不能| Kestrel 預設不認 `.dat` |

## 相關檔案
- `src/Server/Program.cs`

## 發生時間
2026-04-06
