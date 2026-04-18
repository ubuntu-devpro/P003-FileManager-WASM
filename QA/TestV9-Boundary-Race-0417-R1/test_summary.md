# P003 v9 Boundary + Race — TestV9-Boundary-Race-0417-R1

**Date:** 2026-04-17 23:15:36
**Scope:** S8 (12) + S9 (6) — boundary & race conditions
**Total:** 18 | **PASS:** 18 | **FAIL:** 0 | **KNOWN:** 0

| Case | Stage | Name | Status | Note |
|------|-------|------|--------|------|
| EDGE-001 | S8 | Browse empty directory | PASS | code=200 items=[] |
| EDGE-002 | S8 | Browse nonexistent path | PASS | code=200 |
| EDGE-003 | S8 | Special chars in filename (CJK/space/emoji) | PASS | upload=200 landed=True |
| EDGE-004 | S8 | Very long filename (250 chars) | PASS | upload_code=200 landed=True |
| EDGE-005 | S8 | 0-byte file upload + listing size | PASS | upload=200 reported_size=0 |
| EDGE-006 | S8 | Deep nested tree (12 levels) | PASS | code=200 observed_depth=0 |
| EDGE-007 | S8 | DELETE with empty body | PASS | code=415 expected 400/415 |
| EDGE-008 | S8 | Malformed JSON body | PASS | code=400 stack_leak=False |
| EDGE-009 | S8 | Wrong Content-Type | PASS | code=415 |
| EDGE-010 | S8 | DELETE with empty paths array | PASS | code=200 |
| EDGE-011 | S8 | MOVE with empty sourcePaths | PASS | code=200 |
| EDGE-012 | S8 | Search with wildcard chars '*?' | PASS | code=200 |
| RACE-001 | S9 | Concurrent rename of same file | PASS | codes=[200, 400] files_left=['race001_A.txt'] |
| RACE-002 | S9 | Concurrent delete of same file | PASS | codes=[200, 200] file_gone=True |
| RACE-003 | S9 | Delete file while downloading | PASS | dl=200 bytes=5242880 del=200 err= |
| RACE-004 | S9 | Concurrent upload of same filename | PASS | codes={'a': 200, 'b': 200} content_size=1024 pure=True |
| RACE-005 | S9 | Browse while deleting | PASS | list_codes={200} del=200 |
| RACE-006 | S9 | Admin + user concurrent ops on same domain | PASS | codes=[200, 200] |