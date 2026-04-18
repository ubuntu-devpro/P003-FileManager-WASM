# P003 v7 Security + JWT Test — TestV7-Security-JWT-0417-R1

**Date:** 2026-04-17 23:15:35
**Scope:** S7 (14) + S12 (6) — functional completeness for security & auth
**Total:** 20 | **PASS:** 16 | **FAIL:** 0 | **KNOWN:** 4

| Case | Stage | Name | Status | Note |
|------|-------|------|--------|------|
| SEC-001 | S7 | URL-encoded ../ traversal | PASS | code=403, expected=[403, 400] |
| SEC-002 | S7 | Double-encoded ../ traversal | PASS | code=403, expected=[403, 400] |
| SEC-003 | S7 | Backslash ..\ traversal | PASS | code=403, expected=[403, 400] |
| SEC-004 | S7 | Null-byte injection | PASS | code=400, expected=[403, 400, 404] |
| SEC-005 | S7 | Ultra-long path (4096 chars) | PASS | code=403 |
| SEC-006 | S7 | Folder name contains '../' | PASS | code=400, expected=400 |
| SEC-007 | S7 | Rename newName contains path separator | PASS | code=400, expected=400 |
| SEC-008 | S7 | Upload filename with null byte | PASS | code=200, landed_exe=[] |
| SEC-009 | S7 | Double extension malware.exe.txt | PASS | code=200, landed=True (extension check only on final .ext — acceptable) |
| SEC-010 | S7 | Upload overwrites existing file silently | KNOWN | code=200, silent_overwrite=True (v3 §8 #3 — UploadController File.Create) |
| SEC-011 | S7 | johnny downloads /etc/passwd | PASS | code=403, leaked_passwd=False |
| SEC-012 | S7 | johnny downloads others.com file | PASS | code=403, content_leaked=False |
| SEC-013 | S7 | Download symlink → /etc/passwd | KNOWN | code=200, passwd_leaked=True (symlink resolution not blocked — known gap) |
| SEC-014 | S7 | CORS rogue Origin | KNOWN | allow_any_or_rogue=True (Program.cs AllowAnyOrigin — CSRF risk) |
| JWT-001 | S12 | Tampered payload (role=Admin) | PASS | code=401, expected=401 |
| JWT-002 | S12 | Expired token (exp in past) | PASS | code=401, expected=401 |
| JWT-003 | S12 | Different issuer | PASS | code=401, expected=401 |
| JWT-004 | S12 | Different audience | PASS | code=401, expected=401 |
| JWT-005 | S12 | Empty-string token | PASS | code=401, expected=401 |
| JWT-006 | S12 | Token valid after logout (stateless) | KNOWN | code=200, still_works=True (no blacklist — documented limitation) |

## Legend
- **PASS** — behavior matches expected security guarantee
- **FAIL** — regression / newly-introduced gap, must fix
- **KNOWN** — pre-documented limitation (v3 §8), tracked separately, not a regression