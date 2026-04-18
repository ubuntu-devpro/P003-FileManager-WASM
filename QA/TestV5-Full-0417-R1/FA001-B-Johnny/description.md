# FA001-B-Johnny: johnny@sinopac.com login

## Test Info

| Field | Value |
|-------|-------|
| Date | 2026-04-17 |
| Tester | Claude (Automated) |
| Case ID | FA001-B-Johnny |
| Case Name | johnny@sinopac.com login |
| Stage | S1 |
| Environment | Ubuntu-Devpro (VM) |
| APP URL | http://localhost:5001 |
| Test Run | TestV5-Full-0417-R1 |

## Result

| Check | Status |
|-------|--------|
| API | PASS |
| UI | PASS |
| **Overall** | **PASS** |

## Note



## Details

```json
{
  "http_code": 200,
  "jwt_role_correct": true,
  "jwt_domain_correct": true,
  "jwt_claims": {
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "johnny@sinopac.com",
    "http://schemas.microsoft.com/ws/2008/06/identity/claims/role": "User",
    "domain": "sinopac.com",
    "exp": 1776518078,
    "iss": "FileManager.Server",
    "aud": "FileManager.Client"
  }
}
```

## Screenshots

| # | File | Description | Status |
|---|------|-------------|--------|
| 001 | screenshots/001_login_page.png | 001_login_page.png | PASS |
| 002 | screenshots/002_login_success.png | 002_login_success.png | PASS |

## Verdict

- PASS — johnny@sinopac.com login
