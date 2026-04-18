# P003-FileManager-WASM 系統架構設計文件

> 產生日期：2026-04-11

---

## 1. 專案概覽

本專案為一套 **Blazor WebAssembly + ASP.NET Core** 的網頁檔案管理系統，具備 JWT 認證、多租戶（Multi-tenant）隔離、角色存取控制（Admin / User），以及完整的檔案 CRUD 操作。

### 技術棧

| 層級 | 技術 | 版本 |
|------|------|------|
| 前端 | Blazor WebAssembly | .NET 8.0 |
| UI 框架 | Radzen.Blazor | 10.2.0 |
| 後端 | ASP.NET Core Web API | .NET 8.0 |
| 認證 | JWT Bearer (HS256) | 8.0.0 |
| 共用層 | .NET Class Library | .NET 8.0 |

---

## 2. 目錄結構

```
P003-FileManager-WASM/
├── FileManager.sln
├── src/
│   ├── Server/                      # 後端 REST API
│   │   ├── Controllers/
│   │   │   ├── AuthController.cs    # 認證端點
│   │   │   ├── FilesController.cs   # 檔案操作端點
│   │   │   ├── FoldersController.cs # 資料夾建立端點
│   │   │   └── UploadController.cs  # 上傳端點
│   │   ├── Models/
│   │   │   └── User.cs             # 使用者模型 & 登入 DTO
│   │   ├── Services/
│   │   │   ├── JwtService.cs        # JWT 產生 & 驗證
│   │   │   └── FileService.cs       # 檔案系統操作邏輯
│   │   ├── Program.cs              # 服務註冊 & 中介軟體
│   │   └── appsettings.json
│   │
│   ├── Client/                      # 前端 Blazor WASM
│   │   ├── Pages/
│   │   │   ├── Index.razor          # 主檔案管理頁面 (744 行)
│   │   │   └── Login.razor          # 登入頁面
│   │   ├── Components/
│   │   │   ├── FolderTree.razor     # 側邊欄樹狀目錄
│   │   │   ├── TreeNodeItem.razor   # 樹狀節點元件
│   │   │   ├── FmContextMenu.razor  # 右鍵選單元件
│   │   │   ├── NewFolderDialog.razor
│   │   │   └── RenameDialog.razor
│   │   ├── Layout/
│   │   │   └── MainLayout.razor     # 根版面配置
│   │   ├── Services/
│   │   │   └── AuthService.cs       # 客戶端認證狀態管理
│   │   ├── Program.cs              # WASM 主機設定
│   │   └── wwwroot/index.html
│   │
│   └── Shared/                      # 前後端共用 DTO
│       └── Models/Dtos.cs
│
├── tests/
│   └── Server.Tests/               # 後端單元測試
└── QA/                              # QA 測試報告
```

---

## 3. 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                     瀏覽器 (Browser)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Blazor WebAssembly Client                │   │
│  │                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │   │
│  │  │ Login.razor │  │ Index.razor│  │  Components   │  │   │
│  │  │  (登入頁)   │  │ (檔案管理) │  │ FolderTree    │  │   │
│  │  └────────────┘  └─────┬──────┘  │ ContextMenu   │  │   │
│  │                        │         │ TreeNodeItem   │  │   │
│  │                   AuthService    └───────────────┘  │   │
│  │                  (JWT Token 管理)                    │   │
│  └────────────────────────┬─────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP + Bearer Token
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  ASP.NET Core Server                        │
│                                                             │
│  Middleware Pipeline:                                       │
│  ┌─────────┐  ┌────────────────┐  ┌──────────────────┐    │
│  │  CORS   │→ │ Authentication │→ │  Authorization   │    │
│  └─────────┘  └────────────────┘  └───────┬──────────┘    │
│                                           │                │
│  ┌────────────────────────────────────────┼──────────────┐ │
│  │              Controllers               ▼              │ │
│  │  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐  │ │
│  │  │   Auth   │ │  Files   │ │Folders │ │  Upload  │  │ │
│  │  │ /api/auth│ │/api/files│ │/api/   │ │/api/     │  │ │
│  │  │          │ │          │ │folders │ │upload    │  │ │
│  │  └────┬─────┘ └────┬─────┘ └───┬────┘ └────┬─────┘  │ │
│  └───────┼────────────┼───────────┼───────────┼─────────┘ │
│          ▼            ▼           ▼           ▼           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Services                           │  │
│  │  ┌──────────────┐         ┌──────────────────┐      │  │
│  │  │  JwtService  │         │   FileService    │      │  │
│  │  │ (認證/Token)  │         │ (檔案系統操作)    │      │  │
│  │  └──────────────┘         └────────┬─────────┘      │  │
│  └────────────────────────────────────┼─────────────────┘  │
└───────────────────────────────────────┼─────────────────────┘
                                        ▼
                              ┌─────────────────┐
                              │   File System   │
                              │ /home/devpro/data│
                              │  ├── sinopac.com │
                              │  ├── others.com  │
                              │  └── ...         │
                              └─────────────────┘
```

---

## 4. 後端架構

### 4.1 中介軟體管線 (Middleware Pipeline)

```
Request → CORS → Authentication → Authorization → Static Files → Controllers → Response
                                                         ↓
                                              MapFallbackToFile("index.html")
```

**WASM MIME 類型支援：**
- `.wasm` → `application/wasm`
- `.br` → `application/brotli`
- `.dll` → `application/octet-stream`
- `.dat` → `application/octet-stream`

### 4.2 API 端點一覽

#### AuthController (`/api/auth`)

| Method | Route | 需認證 | 說明 |
|--------|-------|--------|------|
| POST | `/login` | 否 | 帳號密碼登入，回傳 JWT Token |
| GET | `/session` | 是 | 驗證 Token 有效性，回傳使用者資訊 |
| POST | `/logout` | 是 | 登出（無狀態 JWT，僅通知） |

#### FilesController (`/api/files`)

| Method | Route | 說明 |
|--------|-------|------|
| GET | `/` | 列出目錄內容 (query: `path`) |
| GET | `/tree` | 取得樹狀資料夾結構 |
| POST | `/search` | 搜尋檔案 (body: `SearchRequest`) |
| PATCH | `/rename` | 重新命名 (body: `RenameRequest`) |
| PATCH | `/move` | 移動檔案/資料夾 (body: `MoveRequest`) |
| DELETE | `/` | 刪除檔案/資料夾 (body: `DeleteRequest`) |
| GET | `/download` | 下載檔案 (query: `path`) |

#### FoldersController (`/api/folders`)

| Method | Route | 說明 |
|--------|-------|------|
| POST | `/` | 建立新資料夾 (query: `path`, `name`) |

#### UploadController (`/api/upload`)

| Method | Route | 說明 |
|--------|-------|------|
| POST | `/` | 上傳檔案 (form: `destinationPath`, `files[]`) |

### 4.3 JWT 認證機制

```
Token 設定:
  - 演算法: HS256
  - 有效期: 24 小時
  - Issuer: FileManager.Server
  - Audience: FileManager.Client

Token Claims:
  - email      → 使用者信箱
  - role       → "Admin" 或 "User"
  - domain     → 租戶網域 (如 sinopac.com)
```

**硬編碼測試帳號：**

| Email | 密碼 | 角色 | Domain |
|-------|------|------|--------|
| admin@devpro.com.tw | admin123 | Admin | devpro.com.tw |
| johnny@sinopac.com | johnny123 | User | sinopac.com |
| user@others.com | user123 | User | others.com |

### 4.4 多租戶存取控制

```
Admin 使用者:
  根路徑 = /home/devpro/data          (完整存取)

一般使用者:
  根路徑 = /home/devpro/data/{domain}  (僅限所屬 domain)

範例:
  johnny@sinopac.com → 只能存取 /home/devpro/data/sinopac.com/
```

### 4.5 安全機制

| 機制 | 說明 |
|------|------|
| 路徑穿越防護 | `IsPathAllowed()` 驗證完整路徑是否在根目錄下 |
| 副檔名黑名單 | 封鎖 `.exe`, `.dll`, `.config` |
| JWT 驗證 | 所有檔案操作端點需 `[Authorize]` |
| 多租戶隔離 | 依 domain claim 限制目錄存取範圍 |

---

## 5. 前端架構

### 5.1 元件層級

```
App.razor (路由)
└── MainLayout.razor (Radzen 主題 + 服務)
    ├── Login.razor (/login)
    │   └── AuthService (登入/登出)
    │
    └── Index.razor (/) ─── 主檔案管理介面
        ├── FolderTree.razor (側邊欄樹狀目錄)
        │   └── TreeNodeItem.razor (遞迴節點)
        ├── FmContextMenu.razor (右鍵選單)
        ├── 工具列 (新增/上傳/下載/刪除/移動/重新命名)
        ├── 麵包屑導航 (Breadcrumb)
        ├── 檔案列表 (Table + Checkbox 多選)
        ├── 上傳對話框 (進度條)
        └── 移動對話框 (資料夾瀏覽器)
```

### 5.2 AuthService 客戶端認證

```csharp
AuthState:
  - Email, IsAdmin, Domain, Token
  - IsAuthenticated (Token 非空即為已登入)

流程:
  1. 登入 → POST /api/auth/login → 取得 Token
  2. Token 儲存至 localStorage ("fm_token")
  3. 設定 HttpClient Bearer Header
  4. 後續請求自動攜帶 Token
  5. 頁面載入 → CheckSessionAsync() 還原登入狀態
```

### 5.3 主要功能

| 功能 | 操作方式 |
|------|----------|
| 瀏覽目錄 | 雙擊資料夾 / 點擊樹狀目錄 / 麵包屑導航 |
| 新增資料夾 | 工具列按鈕 → 輸入名稱對話框 |
| 上傳檔案 | 工具列按鈕 → 多檔選擇 → 進度條 |
| 下載 | 單檔或批次下載 |
| 刪除 | 勾選 → 確認對話框 → 批次刪除 |
| 移動 | 勾選 → 資料夾瀏覽器選目的地 → 批次移動 |
| 重新命名 | 右鍵選單 / 工具列 |
| 搜尋 | 即時搜尋框，依檔名模糊比對 |
| 右鍵選單 | 資料夾：開啟/重新命名/刪除；檔案：下載/重新命名/刪除 |
| 全選/取消 | Checkbox 批次選取 |

### 5.4 UI 設計

- **Login 頁面：** Material 風格深色漸層背景 (`#1a1a2e` → `#16213e`)，白色卡片
- **檔案管理介面：** 左側 250px 樹狀側邊欄 + 右側主內容區
- **檔案圖示：** 30+ 種副檔名對應 Emoji 圖示
- **主色調：** 藍色系 (`#4F81BD`)

---

## 6. 共用層 (Shared)

所有前後端共用的 DTO 定義於 `Shared/Models/Dtos.cs`：

### Request DTOs

| 名稱 | 欄位 |
|------|------|
| `SearchRequest` | Path, Query |
| `RenameRequest` | CurrentPath, NewName |
| `MoveRequest` | SourcePaths[], DestinationPath |
| `DeleteRequest` | Paths[] |

### Response DTOs

| 名稱 | 欄位 |
|------|------|
| `ApiResponse` | Success, Message |
| `FileItem` | Name, Path, IsDirectory, Size, Modified |
| `FileListResponse` | Success, Message, Items[], CurrentPath |
| `FolderTreeNode` | Name, Path, Children[] |
| `FolderTreeResponse` | Success, Message, Nodes[] |
| `UploadResponse` | Success, Message, TotalUploaded |
| `SearchResponse` | Success, Message, Results[] |

---

## 7. 資料流程圖

### 7.1 登入流程

```
瀏覽器                          伺服器
  │                               │
  │  POST /api/auth/login         │
  │  { email, password }          │
  │──────────────────────────────▶│
  │                               │── JwtService.ValidateCredentials()
  │                               │── JwtService.GenerateToken()
  │  { success, token, email,     │
  │    isAdmin, domain }          │
  │◀──────────────────────────────│
  │                               │
  │  localStorage.set("fm_token") │
  │  設定 Bearer Header           │
  │  導向 /                       │
```

### 7.2 檔案列表流程

```
瀏覽器                                    伺服器
  │                                         │
  │  GET /api/files?path=xxx                │
  │  Authorization: Bearer {token}          │
  │────────────────────────────────────────▶│
  │                                         │── 解析 JWT Claims
  │                                         │── GetRootPathForUser() 多租戶邏輯
  │                                         │── FileService.GetFilesAsync()
  │                                         │── 讀取檔案系統
  │  { success, items[], currentPath }      │
  │◀────────────────────────────────────────│
  │                                         │
  │  渲染檔案列表表格                        │
```

### 7.3 上傳流程

```
瀏覽器                                    伺服器
  │                                         │
  │  使用者選擇檔案                          │
  │  逐檔 POST /api/upload                  │
  │  Content-Type: multipart/form-data      │
  │  { destinationPath, files[] }           │
  │────────────────────────────────────────▶│
  │                                         │── IsPathAllowed() 路徑驗證
  │                                         │── File.Create() 寫入磁碟
  │  { success, totalUploaded }             │
  │◀────────────────────────────────────────│
  │                                         │
  │  更新進度條                              │
  │  重新載入檔案列表                         │
```

---

## 8. 已知安全注意事項

| 項目 | 現況 | 建議 |
|------|------|------|
| JWT Secret Key | 硬編碼在程式碼中 | 移至環境變數或 Key Vault |
| 使用者密碼 | 明文儲存在 JwtService | 導入資料庫 + bcrypt 雜湊 |
| 使用者帳號 | 硬編碼三組測試帳號 | 導入資料庫管理 |
| CORS 設定 | `AllowAnyOrigin()` 全開 | 上線前改回白名單模式 |
| Token 儲存 | localStorage（易受 XSS） | 考慮 HttpOnly Cookie |
| API URL | 前端硬編碼 `localhost:5001` | 改用環境設定或相對路徑 |
| 速率限制 | 無 | 加入登入端點的速率限制 |
| 稽核日誌 | 無 | 加入操作紀錄 |

---

## 9. 關鍵檔案速查

| 檔案 | 行數 | 用途 |
|------|------|------|
| `src/Server/Program.cs` | 71 | 服務註冊、中介軟體管線 |
| `src/Server/Services/JwtService.cs` | 58 | JWT Token 產生與帳密驗證 |
| `src/Server/Services/FileService.cs` | 227 | 檔案系統操作（列表/搜尋/移動/刪除） |
| `src/Server/Controllers/AuthController.cs` | 64 | 登入/登出/Session 端點 |
| `src/Server/Controllers/FilesController.cs` | 92 | 檔案操作 API 端點 |
| `src/Server/Controllers/FoldersController.cs` | 25 | 建立資料夾端點 |
| `src/Server/Controllers/UploadController.cs` | 47 | 檔案上傳端點 |
| `src/Server/Models/User.cs` | ~30 | 使用者模型 & 登入 DTO |
| `src/Client/Pages/Index.razor` | 744 | 主檔案管理介面（最大元件） |
| `src/Client/Pages/Login.razor` | ~120 | 登入頁面 |
| `src/Client/Services/AuthService.cs` | 119 | 客戶端認證狀態管理 |
| `src/Client/Components/FolderTree.razor` | ~50 | 樹狀目錄元件 |
| `src/Client/Components/TreeNodeItem.razor` | ~40 | 樹狀節點遞迴元件 |
| `src/Client/Components/FmContextMenu.razor` | ~60 | 右鍵選單元件 |
| `src/Shared/Models/Dtos.cs` | 46 | 所有 Request/Response DTO |
