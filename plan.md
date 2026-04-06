# P003-FileManager-WASM 翻寫計畫

## 目標
驗證 AI + 人力協作，翻寫一個無 SignalR 的檔案管理器

## 架構原則
- **無 SignalR** — Blazor WebAssembly + REST API
- **自動化優先** — Playwright 截圖要能穩定跑
- **簡單直接** — 不需要的東西一律不加

## 技術選型
| 層 | 技術 | 理由 |
|----|------|------|
| 前端 UI | Blazor WebAssembly | 客戶端跑，無 SignalR，自動化友好 |
| 後端 API | ASP.NET Core Web API | 純 REST，無 Blazor |
| UI 框架 | Radzen Blazor（WebAssembly 版）| 免費 MIT |
| 認證 | JWT Token | 無 session cookie，無電路問題 |
| 測試 | Playwright | 穩定，無電路中斷問題 |

## 功能對照（對齊 P002）

| 編號 | 功能 | P002 狀態 | P003 目標 |
|------|------|-----------|-----------|
| FM-001 | 資料夾瀏覽 | ✅ 完成 | ✅ |
| FM-002 | 建立資料夾 | ✅ 完成 | ✅ |
| FM-003 | 重新命名 | ✅ 完成 | ✅ |
| FM-004 | 移動檔案 | ✅ 完成 | ✅ |
| FM-005 | 刪除 | ✅ 完成 | ✅ |
| FM-006 | 單一上傳 | ✅ 完成 | ✅ |
| FM-007 | 多重上傳 | ✅ 完成 | ✅ |
| FM-008 | 拖拉上傳 | ❌ 未實作 | ✅ |
| FM-009 | 下載 | ✅ 完成 | ✅ |
| FM-010 | 多重下載 | ✅ 完成 | ✅ |
| FM-011 | 搜尋 | ✅ 完成 | ✅ |

## 開發流程
1. Server API 先完成（SIT 測試）
2. Client UI 上 WebAssembly
3. E2E Playwright 截圖（這次要穩）
4. QA 報告

## Repo
https://github.com/ubuntu-devpro/P003-FileManager-WASM
