#!/usr/bin/env python3
"""
P003-FileManager-WASM — v12 AdminDomains Feature Test
測試 AdminDomains 設定：指定 domain 下所有使用者自動取得 Admin 角色
"""
import subprocess, json, os, time

# === Config ===
API_URL = "http://localhost:5001"
QA_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA"
TEST_RUN = f"TestV12-AdminDomain-0418-R1"
CASES_DIR = f"{QA_DIR}/{TEST_RUN}"

# 測試情境定義
# expected_login: True=登入成功, False=被拒絕
# expected_admin: True=Admin, False=一般使用者, None=不適用(登入失敗)
TEST_CASES = [
    {
        "id": "AD-001",
        "name": "AdminEmails 命中 → Admin",
        "email": "admin@devpro.com.tw",
        "password": "admin123",
        "expected_login": True,
        "expected_admin": True,
        "reason": "email 在 AdminEmails 清單內",
    },
    {
        "id": "AD-002",
        "name": "AdminDomains 命中（非 AdminEmails）→ Admin",
        "email": "abc@devpro.com.tw",
        "password": "abc123",
        "expected_login": True,
        "expected_admin": True,
        "reason": "domain devpro.com.tw 在 AdminDomains，但 email 不在 AdminEmails",
    },
    {
        "id": "AD-003",
        "name": "AllowedDomains 但非 AdminDomains → User",
        "email": "user@msn.com",
        "password": "msn123",
        "expected_login": True,
        "expected_admin": False,
        "reason": "msn.com 在 AllowedEmailDomains 但不在 AdminDomains",
    },
    {
        "id": "AD-004",
        "name": "不在 AllowedEmailDomains → 拒絕登入",
        "email": "johnny@sinopac.com",
        "password": "johnny123",
        "expected_login": False,
        "expected_admin": None,
        "reason": "sinopac.com 不在 AllowedEmailDomains",
    },
    {
        "id": "AD-005",
        "name": "AdminDomains 大小寫不分 → Admin",
        "email": "ABC@DEVPRO.COM.TW",
        "password": "abc123",
        "expected_login": True,
        "expected_admin": True,
        "reason": "domain 比對應 case-insensitive",
    },
]

results = []


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def api_call(method, endpoint, data=None, token=None):
    url = f"{API_URL}{endpoint}"
    cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method]
    if token:
        cmd += ["-H", f"Authorization: Bearer {token}"]
    if data:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        lines = r.stdout.strip().rsplit("\n", 1)
        body = lines[0] if len(lines) > 1 else ""
        code = int(lines[-1]) if lines[-1].isdigit() else 0
        return code, body
    except Exception as e:
        return 0, str(e)


def decode_jwt(token):
    try:
        import base64
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except:
        return {}


def record(case_id, name, passed, note="", details=None):
    status = "PASS" if passed else "FAIL"
    icon = "✅" if passed else "❌"
    print(f"    {icon} [{status}] {case_id}: {name}")
    if note:
        print(f"         {note}")
    results.append({
        "id": case_id, "name": name,
        "status": status, "note": note, "details": details or {}
    })


def run_tests():
    ensure_dir(CASES_DIR)
    print("\n" + "=" * 60)
    print("  P003 v12 — AdminDomains Feature Test")
    print("=" * 60)

    for tc in TEST_CASES:
        print(f"\n  {tc['id']}: {tc['name']}")
        code, body = api_call("POST", "/api/auth/login",
                              {"email": tc["email"], "password": tc["password"]})

        try:
            data = json.loads(body)
        except:
            data = {}

        login_ok = code == 200 and data.get("success") is True
        is_admin = data.get("isAdmin", False)
        token = data.get("token", "")
        jwt_claims = decode_jwt(token) if token else {}
        jwt_role = jwt_claims.get("http://schemas.microsoft.com/ws/2008/06/identity/claims/role", "")

        details = {
            "http_code": code,
            "login_success": login_ok,
            "is_admin": is_admin,
            "jwt_role": jwt_role,
            "reason": tc["reason"],
        }

        if not tc["expected_login"]:
            # 預期被拒絕
            passed = not login_ok
            note = f"http={code}, login={'rejected ✓' if passed else 'accepted ✗'}"
        else:
            # 預期登入成功，再驗證 isAdmin
            login_pass = login_ok
            admin_pass = (is_admin == tc["expected_admin"])
            jwt_role_ok = (jwt_role == "Admin") == tc["expected_admin"]
            passed = login_pass and admin_pass and jwt_role_ok
            note = (f"http={code}, isAdmin={is_admin} (expected={tc['expected_admin']}), "
                    f"jwt_role={jwt_role}")

        record(tc["id"], tc["name"], passed, note, details)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = total - passed
    print("\n" + "=" * 60)
    print(f"  RESULT: {passed}/{total} PASS  |  {failed} FAIL")
    print("=" * 60)

    # Save JSON report
    report_path = f"{CASES_DIR}/results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_run": TEST_RUN,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": total, "passed": passed, "failed": failed,
            "cases": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n  Report: {report_path}")

    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    exit(0 if ok else 1)
