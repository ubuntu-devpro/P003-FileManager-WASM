# P003 v8 Tenant Matrix — TestV8-Tenant-Matrix-0417-R1

**Date:** 2026-04-17 23:15:35
**Scope:** Tenant-isolation matrix fills (Groups A/B/D/E/F/G/H)
**Total:** 28 | **PASS:** 28 | **FAIL:** 0 | **KNOWN:** 0

| Case | Group | Name | Status | Note |
|------|-------|------|--------|------|
| MTX-A01 | A | johnny browse devpro.com.tw | PASS | code=403 |
| MTX-A02 | A | johnny tree devpro.com.tw | PASS | code=403 |
| MTX-A03 | A | johnny create folder in devpro.com.tw | PASS | code=403 |
| MTX-A04 | A | johnny rename file in devpro.com.tw | PASS | code=403 |
| MTX-A05 | A | johnny move FROM devpro TO sinopac | PASS | code=403 |
| MTX-A06 | A | johnny delete file in devpro.com.tw | PASS | code=403 |
| MTX-A07 | A | johnny upload to devpro.com.tw | PASS | code=403 |
| MTX-A08 | A | johnny download from devpro.com.tw | PASS | code=403 |
| MTX-A09 | A | johnny search in devpro.com.tw | PASS | code=403 |
| MTX-B01 | B | user browse root (clamped) | PASS | code=200 names=['tenantmtx', 'hacked', 'test.txt'] |
| MTX-B02 | B | user browse sinopac.com | PASS | code=403 |
| MTX-B03 | B | user browse devpro.com.tw | PASS | code=403 |
| MTX-B04 | B | user tree sinopac.com | PASS | code=403 |
| MTX-B05 | B | user upload to sinopac.com | PASS | code=403 |
| MTX-B06 | B | user delete in sinopac.com | PASS | code=403 |
| MTX-B07 | B | user rename in sinopac.com | PASS | code=403 |
| MTX-B08 | B | user move FROM others.com TO sinopac.com (dest cross) | PASS | code=403 |
| MTX-B09 | B | user download sinopac.com file | PASS | code=403 |
| MTX-D01 | D | johnny move FROM others.com TO sinopac (source cross) | PASS | code=403 |
| MTX-D02 | D | johnny mixed-source move (own + foreign) | PASS | code=403 |
| MTX-E01 | E | johnny rename file in others.com | PASS | code=403 |
| MTX-F01 | F | johnny rename sinopac.com (own root) | PASS | code=403 |
| MTX-F02 | F | johnny delete sinopac.com (own root) | PASS | code=403 |
| MTX-F03 | F | johnny move sinopac.com folder to /data root | PASS | code=403 |
| MTX-G01 | G | johnny traversal sinopac/../others | PASS | code=403 |
| MTX-H01 | H | admin browse all 3 domains | PASS | all domains browsable |
| MTX-H02 | H | admin download sinopac marker | PASS | code=200 |
| MTX-H03 | H | admin move sinopac → devpro | PASS | code=200 |