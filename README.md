# P003-FileManager-WASM

檔案管理器 — Blazor WebAssembly 翻寫（無 SignalR）

## 架構

- **前端：** Blazor WebAssembly（客戶端渲染，無 SignalR，自動化測試友好）
- **後端：** ASP.NET Core Web API（純 REST，無 Blazor）
- **通訊：** HTTP JSON，無 WebSocket
- **RootFolder：** `/home/devpro/data`

## 專案結構

```
src/
├── Server/          # ASP.NET Core Web API
│   ├── Controllers/  FilesController, FoldersController, UploadController
│   └── Services/     IFileService, FileService（路徑遍歷防護）
├── Client/          # Blazor WebAssembly
│   ├── Pages/        Index.razor（主頁面）
│   └── Services/     IFileServiceClient
└── Shared/          # DTOs（Request/Response models）
```

## 執行

```bash
# 啟動 API Server（port 5001）
cd src/Server && dotnet run --urls "http://localhost:5001"

# 啟動 Blazor WASM Client（port 5000，開發模式）
cd src/Client && dotnet run
```

## API 端點

| Method | Endpoint | 說明 |
|--------|----------|------|
| GET | `/api/files?path=...` | 列出檔案 |
| GET | `/api/files/tree?path=...` | 資料夾樹 |
| POST | `/api/files/search` | 搜尋 |
| PATCH | `/api/files/rename` | 重新命名 |
| PATCH | `/api/files/move` | 移動 |
| DELETE | `/api/files` | 刪除 |
| POST | `/api/folders?path=...&name=...` | 建立資料夾 |
| POST | `/api/upload` | 上傳檔案 |

## 功能對照

| FM | 功能 | 狀態 |
|----|------|------|
| FM-001 | 資料夾瀏覽 | 🚧 建置中 |
| FM-002 | 建立資料夾 | 🚧 建置中 |
| FM-003 | 重新命名 | 🚧 建置中 |
| FM-004 | 移動 | 🚧 建置中 |
| FM-005 | 刪除 | 🚧 建置中 |
| FM-006 | 單一上傳 | 🚧 建置中 |
| FM-007 | 多重上傳 | 🚧 建置中 |
| FM-008 | 拖拉上傳 | 🚧 建置中 |
| FM-009 | 下載 | 🚧 建置中 |
| FM-010 | 多重下載 | 🚧 建置中 |
| FM-011 | 搜尋 | 🚧 建置中 |

## 與 P002 的差異

| 項目 | P002（Blazor Server）| P003（WASM）|
|------|---------------------|-------------|
| SignalR | 有（電路問題）| 無 |
| 自動化測試 | ❌ 不穩定 | ✅ 穩定 |
| 架構複雜度 | 高（SSR + 電路）| 低（純客戶端）|
