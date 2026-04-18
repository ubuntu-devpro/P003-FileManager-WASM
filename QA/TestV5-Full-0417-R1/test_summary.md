# P003 Full Test v5 Summary — TestV5-Full-0417-R1

**Date:** 2026-04-17 21:20:02
**Tester:** Claude (Automated)
**Total:** 54 | **PASS:** 54 | **FAIL:** 0

## Stage Results

| Stage | Status |
|-------|--------|
| S1 | ALL PASS |
| S2 | ALL PASS |
| S3 | ALL PASS |
| S4 | ALL PASS |
| S5 | ALL PASS |
| S6 | ALL PASS |

## Case Details

| Case | Name | Stage | API | UI | Status | Note |
|------|------|-------|-----|-----|--------|------|
| FA001-A-Admin | admin@devpro.com.tw login | S1 | PASS | PASS | PASS |  |
| FA001-B-Johnny | johnny@sinopac.com login | S1 | PASS | PASS | PASS |  |
| FA001-C-User | user@others.com login | S1 | PASS | PASS | PASS |  |
| FA002-A-Admin | admin@devpro.com.tw visible scope | S1 | PASS | PASS | PASS |  |
| FA002-B-Johnny | johnny@sinopac.com visible scope | S1 | PASS | PASS | PASS |  |
| FA002-C-User | user@others.com visible scope | S1 | PASS | PASS | PASS |  |
| FA003 | Logout | S1 | PASS | PASS | PASS |  |
| FA004-A | Session: valid token | S1 | PASS | PASS | PASS | code=200, expected=[200] |
| FA004-B | Session: invalid token | S1 | PASS | PASS | PASS | code=401, expected=[401] |
| FA004-C | Session: no token files API | S1 | PASS | PASS | PASS | code=401, expected=[401] |
| MT001-A | johnny access root | S2 | PASS | PASS | PASS | code=200 |
| MT001-B | johnny access others.com | S2 | PASS | PASS | PASS | code=403 |
| MT001-C | johnny path traversal | S2 | PASS | PASS | PASS | code=403 |
| MT001-D | johnny access /etc/passwd | S2 | PASS | PASS | PASS | code=403 |
| MT002-A | johnny upload to others.com | S2 | PASS | PASS | PASS | code=403 |
| MT002-B | johnny create folder in others.com | S2 | PASS | PASS | PASS | code=403 |
| MT002-C | johnny delete in others.com | S2 | PASS | PASS | PASS | code=403 |
| MT002-D | johnny move to others.com | S2 | PASS | PASS | PASS | code=403 |
| MT003-A | johnny download from others.com | S2 | PASS | PASS | PASS | code=403 |
| MT003-B | johnny search isolation | S2 | PASS | PASS | PASS | found_others=False |
| FM001 | Folder Browse | S3 | PASS | PASS | PASS |  |
| FM002 | Create Folder | S3 | PASS | PASS | PASS | api_verified=True |
| FM003 | Rename | S3 | PASS | PASS | PASS |  |
| FM004 | Move File | S3 | PASS | PASS | PASS |  |
| FM005 | Delete | S3 | PASS | PASS | PASS |  |
| FM006 | Single Upload | S3 | PASS | PASS | PASS | verified=True |
| FM007 | Multi Upload | S3 | PASS | PASS | PASS |  |
| FM008 | Drag Upload (element check) | S3 | PASS | PASS | PASS |  |
| FM009 | Single Download | S3 | PASS | PASS | PASS |  |
| FM010 | Multi Download | S3 | PASS | PASS | PASS |  |
| FM011 | Search | S3 | PASS | PASS | PASS |  |
| FM001-U | Johnny browse own domain | S4 | PASS | PASS | PASS |  |
| FM002-U | Johnny create folder | S4 | PASS | PASS | PASS | verified=True |
| FM003-U | Johnny rename in own domain | S4 | PASS | PASS | PASS | code=200 |
| FM005-U | Johnny delete in own domain | S4 | PASS | PASS | PASS | code=200 |
| FM006-U | Johnny upload to own domain | S4 | PASS | PASS | PASS | verified=True |
| FM009-U | Johnny download from own domain | S4 | PASS | PASS | PASS | code=200 |
| FM011-U | Johnny search (scoped) | S4 | PASS | PASS | PASS | has_cross_tenant=False |
| CA001 | Admin root folder invisible to johnny | S5 | PASS | PASS | PASS | johnny_sees=False |
| CA002 | Admin sinopac.com folder visible to johnny | S5 | PASS | PASS | PASS | johnny_sees=True |
| CA003 | Johnny upload visible to admin | S5 | PASS | PASS | PASS | admin_sees=True |
| CA004 | Johnny file invisible to user@others.com | S5 | PASS | PASS | PASS | user_sees=False, code=403 |
| NE001-A | wrong password | S6 | PASS | PASS | PASS | code=401, got_token=False |
| NE001-B | nonexistent account | S6 | PASS | PASS | PASS | code=401, got_token=False |
| NE001-C | empty credentials | S6 | PASS | PASS | PASS | code=400, got_token=False |
| NE001-D | SQL injection | S6 | PASS | PASS | PASS | code=401, got_token=False |
| NE001-A-UI | Wrong password UI | S6 | PASS | PASS | PASS |  |
| NE002-A | duplicate folder name | S6 | PASS | PASS | PASS | code=400 |
| NE002-B | rename to empty string | S6 | PASS | PASS | PASS | code=400 |
| NE002-C | rename with path traversal | S6 | PASS | PASS | PASS | code=400 |
| NE002-D | delete nonexistent | S6 | PASS | PASS | PASS | code=200 |
| NE002-G | search empty query | S6 | PASS | PASS | PASS | code=200 |
| NE002-E | upload .exe blocked | S6 | PASS | PASS | PASS | code=200 |
| NE002-F | upload empty file | S6 | PASS | PASS | PASS | code=200 |
