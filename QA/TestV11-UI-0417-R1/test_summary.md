# P003 v11 UI State — TestV11-UI-0417-R1

**Date:** 2026-04-17 23:15:30
**Scope:** S11 (8) — UI state & interaction completeness
**Total:** 8 | **PASS:** 8 | **FAIL:** 0

| Case | Name | Status | Note |
|------|------|--------|------|
| UI-001 | Escape 關閉 dialog | PASS | dialog_closed=True |
| UI-002 | 重新整理後不留 orphan dialog | PASS | orphan_dialog=False |
| UI-003 | 快速雙擊不重複觸發 API | PASS | api_calls_fired=1 (expect 1-2) |
| UI-004 | 全選取消全選 selectedPaths 清空 | PASS | rows=42 after_select=42 after_deselect=0 |
| UI-005 | 右鍵選單外點擊關閉 | PASS | menu_was_open=True menu_now_closed=True |
| UI-006 | 上傳dialog取消無殘留 | PASS | was_open=True dialog_gone=True progress_gone=True |
| UI-007 | 網路斷線不白畫面 | PASS | has_content=True has_error_msg=True |
| UI-008 | Token過期跳登入頁 | PASS | url=http://localhost:5001/ login_form=True |