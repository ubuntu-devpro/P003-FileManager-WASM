#!/usr/bin/env python3
"""
P003-FileManager-WASM — v8 Tenant Isolation Matrix Test
Fills the cross-domain matrix gaps identified after v5+v7:
  A: johnny → devpro.com.tw (admin domain, wholly missing)
  B: user@others.com as attacker (3rd account, wholly missing)
  C: Tree API cross-domain
  D: Move reverse / mixed source
  E: Rename cross-domain
  F: Operations on domain-root folders themselves
  G: Path normalization boundary
  H: Admin sanity across domains
"""
import subprocess, json, os, time, urllib.parse
import requests

API_URL = "http://localhost:5001"
ROOT = "/home/devpro/data"
QA_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA"
TEST_RUN = "TestV8-Tenant-Matrix-0417-R1"
CASES_DIR = f"{QA_DIR}/{TEST_RUN}"

ACCOUNTS = {
    "admin":  {"email": "admin@devpro.com.tw",  "password": "admin123",  "domain": "devpro.com.tw"},
    "johnny": {"email": "johnny@sinopac.com",   "password": "johnny123", "domain": "sinopac.com"},
    "user":   {"email": "user@others.com",      "password": "user123",   "domain": "others.com"},
}
DOMAINS = {
    "admin":  f"{ROOT}/devpro.com.tw",
    "johnny": f"{ROOT}/sinopac.com",
    "user":   f"{ROOT}/others.com",
}

results = []
tokens  = {}


def ensure_dir(p): os.makedirs(p, exist_ok=True)


def login(key):
    acc = ACCOUNTS[key]
    r = requests.post(f"{API_URL}/api/auth/login",
                      json={"email": acc["email"], "password": acc["password"]}, timeout=15)
    if r.status_code == 200:
        tokens[key] = r.json().get("token", "")
        return True
    return False


def hdr(key): return {"Authorization": f"Bearer {tokens[key]}"}


def record(case_id, group, name, status, note=""):
    results.append({"case": case_id, "group": group, "name": name, "status": status, "note": note})
    tag = {"PASS": "PASS", "FAIL": "FAIL", "KNOWN": "KNOWN", "SKIP": "SKIP"}.get(status, status)
    print(f"    [{tag}] {case_id}: {name} — {note}")


def check_deny(case_id, group, name, resp, extra_forbidden=None):
    """A deny-path test: expect 403/404/400 AND response must not leak the target content."""
    code = resp.status_code
    body = resp.text
    ok = code in (403, 400, 404)
    if ok and extra_forbidden:
        for s in extra_forbidden:
            if s and s in body:
                ok = False
                break
    status = "PASS" if ok else "FAIL"
    record(case_id, group, name, status, f"code={code}")
    return ok


def check_allow(case_id, group, name, resp):
    ok = 200 <= resp.status_code < 300
    status = "PASS" if ok else "FAIL"
    record(case_id, group, name, status, f"code={resp.status_code}")
    return ok


# ============================================================
# Setup: plant one test file in each domain via admin
# ============================================================

SETUP_FILES = {}  # key=owner_domain, value=absolute path


def setup_fixtures():
    print("\n[setup] planting test files via admin")
    a = hdr("admin")
    for owner, domain_root in DOMAINS.items():
        # admin can write into every domain root
        # ensure dir exists
        r = requests.post(f"{API_URL}/api/folders",
                          params={"path": domain_root, "name": "tenantmtx"},
                          headers=a, timeout=15)
        # (409/200 both acceptable)
        # upload a marker file
        payload = f"OWNER={owner} MARKER".encode()
        r = requests.post(f"{API_URL}/api/upload",
                          params={"path": f"{domain_root}/tenantmtx"},
                          headers=a,
                          files={"file": (f"marker_{owner}.txt", payload, "text/plain")},
                          timeout=15)
        SETUP_FILES[owner] = f"{domain_root}/tenantmtx/marker_{owner}.txt"
        print(f"  planted: {SETUP_FILES[owner]} (code={r.status_code})")


def teardown_fixtures():
    print("\n[teardown] removing test files via admin")
    a = hdr("admin")
    # delete marker files
    paths = list(SETUP_FILES.values())
    # also delete the tenantmtx folders
    for domain_root in DOMAINS.values():
        paths.append(f"{domain_root}/tenantmtx")
    r = requests.delete(f"{API_URL}/api/files",
                        headers=a,
                        json={"paths": paths}, timeout=15)
    print(f"  teardown code={r.status_code}")


# ============================================================
# Group A: johnny → devpro.com.tw (admin domain) — 9 cases
# ============================================================

def group_a():
    print("\n[A] johnny vs admin domain (devpro.com.tw)")
    t = hdr("johnny")
    dev = DOMAINS["admin"]
    sin = DOMAINS["johnny"]
    victim = SETUP_FILES["admin"]

    # A01: browse
    r = requests.get(f"{API_URL}/api/files", params={"path": dev}, headers=t, timeout=15)
    # ClampPathToUserScope clamps ancestor to user root; devpro.com.tw is a *sibling* → should be 403
    check_deny("MTX-A01", "A", "johnny browse devpro.com.tw", r,
               extra_forbidden=["marker_admin"])

    # A02: tree
    r = requests.get(f"{API_URL}/api/files/tree", params={"path": dev}, headers=t, timeout=15)
    check_deny("MTX-A02", "A", "johnny tree devpro.com.tw", r,
               extra_forbidden=["devpro.com.tw"])

    # A03: create folder inside devpro
    r = requests.post(f"{API_URL}/api/folders",
                      params={"path": dev, "name": "hacked_by_johnny"}, headers=t, timeout=15)
    check_deny("MTX-A03", "A", "johnny create folder in devpro.com.tw", r)

    # A04: rename a file inside devpro
    r = requests.patch(f"{API_URL}/api/files/rename",
                       headers=t, json={"currentPath": victim, "newName": "stolen.txt"}, timeout=15)
    check_deny("MTX-A04", "A", "johnny rename file in devpro.com.tw", r)

    # A05: move a devpro file into sinopac (source cross-domain)
    r = requests.patch(f"{API_URL}/api/files/move",
                       headers=t, json={"sourcePaths": [victim], "destinationPath": sin}, timeout=15)
    check_deny("MTX-A05", "A", "johnny move FROM devpro TO sinopac", r)

    # A06: delete a file in devpro
    r = requests.delete(f"{API_URL}/api/files",
                        headers=t, json={"paths": [victim]}, timeout=15)
    check_deny("MTX-A06", "A", "johnny delete file in devpro.com.tw", r)
    # verify still exists
    r2 = requests.get(f"{API_URL}/api/files", params={"path": f"{dev}/tenantmtx"}, headers=hdr("admin"), timeout=15)
    still_there = "marker_admin.txt" in r2.text
    if not still_there:
        record("MTX-A06-v", "A", "verify devpro file still exists after johnny delete",
               "FAIL", "file was actually deleted!")

    # A07: upload into devpro
    r = requests.post(f"{API_URL}/api/upload",
                      params={"path": dev}, headers=t,
                      files={"file": ("uploaded_by_johnny.txt", b"HACKED", "text/plain")}, timeout=15)
    # Upload endpoint returns 200 with body Success=False OR 403
    if r.status_code == 403:
        record("MTX-A07", "A", "johnny upload to devpro.com.tw", "PASS", "code=403")
    elif r.status_code == 200:
        try:
            j = r.json()
            ok = j.get("success") is False and j.get("filesUploaded", 0) == 0
            record("MTX-A07", "A", "johnny upload to devpro.com.tw",
                   "PASS" if ok else "FAIL",
                   f"code=200 body={j}")
        except Exception:
            record("MTX-A07", "A", "johnny upload to devpro.com.tw", "FAIL",
                   f"code=200 but unparseable body")
    else:
        record("MTX-A07", "A", "johnny upload to devpro.com.tw", "FAIL",
               f"unexpected code={r.status_code}")
    # verify no uploaded file landed
    if os.path.exists(f"{dev}/uploaded_by_johnny.txt"):
        record("MTX-A07-v", "A", "verify no johnny upload landed in devpro",
               "FAIL", "file landed on disk!")
        try: os.remove(f"{dev}/uploaded_by_johnny.txt")
        except: pass

    # A08: download
    r = requests.get(f"{API_URL}/api/files/download",
                     params={"path": victim}, headers=t, timeout=15)
    check_deny("MTX-A08", "A", "johnny download from devpro.com.tw", r,
               extra_forbidden=["OWNER=admin"])

    # A09: search
    r = requests.post(f"{API_URL}/api/files/search",
                      headers=t, json={"path": dev, "query": "marker"}, timeout=15)
    # Search endpoint may return 403 OR 200 with filtered empty list
    if r.status_code == 403:
        record("MTX-A09", "A", "johnny search in devpro.com.tw", "PASS", "code=403")
    else:
        try:
            body = r.json()
            results_list = body.get("results", [])
            leaked = any("marker_admin" in (item.get("path", "") or item.get("name", "")) for item in results_list)
            record("MTX-A09", "A", "johnny search in devpro.com.tw",
                   "FAIL" if leaked else "PASS",
                   f"code={r.status_code} leaked={leaked} n_results={len(results_list)}")
        except Exception:
            record("MTX-A09", "A", "johnny search in devpro.com.tw",
                   "FAIL", f"code={r.status_code} unparseable")


# ============================================================
# Group B: user@others.com as attacker (9 cases)
# ============================================================

def group_b():
    print("\n[B] user@others.com attacking other domains")
    t = hdr("user")
    sin = DOMAINS["johnny"]
    dev = DOMAINS["admin"]
    victim_sin = SETUP_FILES["johnny"]
    others = DOMAINS["user"]

    # B01: browse root
    r = requests.get(f"{API_URL}/api/files", params={"path": ROOT}, headers=t, timeout=15)
    # ClampPathToUserScope treats root as ancestor → clamps to others.com (allowed). Must NOT list devpro/sinopac content.
    if r.status_code == 200:
        body_json = {}
        try: body_json = r.json()
        except: pass
        items = body_json.get("items", [])
        names = [it.get("name", "") for it in items]
        leaked = any(n in ("devpro.com.tw", "sinopac.com") for n in names)
        record("MTX-B01", "B", "user browse root (clamped)",
               "FAIL" if leaked else "PASS",
               f"code=200 names={names}")
    else:
        record("MTX-B01", "B", "user browse root", "PASS", f"code={r.status_code}")

    # B02: browse sinopac.com
    r = requests.get(f"{API_URL}/api/files", params={"path": sin}, headers=t, timeout=15)
    check_deny("MTX-B02", "B", "user browse sinopac.com", r, extra_forbidden=["marker_johnny"])

    # B03: browse devpro.com.tw
    r = requests.get(f"{API_URL}/api/files", params={"path": dev}, headers=t, timeout=15)
    check_deny("MTX-B03", "B", "user browse devpro.com.tw", r, extra_forbidden=["marker_admin"])

    # B04: tree sinopac.com
    r = requests.get(f"{API_URL}/api/files/tree", params={"path": sin}, headers=t, timeout=15)
    check_deny("MTX-B04", "B", "user tree sinopac.com", r)

    # B05: upload to sinopac.com
    r = requests.post(f"{API_URL}/api/upload",
                      params={"path": sin}, headers=t,
                      files={"file": ("user_intrusion.txt", b"INTRUDE", "text/plain")}, timeout=15)
    if r.status_code == 403:
        record("MTX-B05", "B", "user upload to sinopac.com", "PASS", "code=403")
    elif r.status_code == 200:
        try:
            j = r.json()
            ok = j.get("success") is False and j.get("filesUploaded", 0) == 0
            record("MTX-B05", "B", "user upload to sinopac.com",
                   "PASS" if ok else "FAIL", f"code=200 body={j}")
        except Exception:
            record("MTX-B05", "B", "user upload to sinopac.com", "FAIL", "unparseable")
    # verify
    if os.path.exists(f"{sin}/user_intrusion.txt"):
        record("MTX-B05-v", "B", "verify no user upload landed in sinopac",
               "FAIL", "file landed!")
        try: os.remove(f"{sin}/user_intrusion.txt")
        except: pass

    # B06: delete in sinopac.com
    r = requests.delete(f"{API_URL}/api/files", headers=t, json={"paths": [victim_sin]}, timeout=15)
    check_deny("MTX-B06", "B", "user delete in sinopac.com", r)
    # verify
    r2 = requests.get(f"{API_URL}/api/files", params={"path": f"{sin}/tenantmtx"}, headers=hdr("admin"), timeout=15)
    if "marker_johnny.txt" not in r2.text:
        record("MTX-B06-v", "B", "verify sinopac file still exists after user delete",
               "FAIL", "file was actually deleted!")

    # B07: rename in sinopac.com
    r = requests.patch(f"{API_URL}/api/files/rename", headers=t,
                       json={"currentPath": victim_sin, "newName": "stolen.txt"}, timeout=15)
    check_deny("MTX-B07", "B", "user rename in sinopac.com", r)

    # B08: move from user's own domain to sinopac (dest cross)
    r = requests.patch(f"{API_URL}/api/files/move", headers=t,
                       json={"sourcePaths": [SETUP_FILES["user"]], "destinationPath": sin}, timeout=15)
    check_deny("MTX-B08", "B", "user move FROM others.com TO sinopac.com (dest cross)", r)

    # B09: download sinopac file
    r = requests.get(f"{API_URL}/api/files/download",
                     params={"path": victim_sin}, headers=t, timeout=15)
    check_deny("MTX-B09", "B", "user download sinopac.com file", r, extra_forbidden=["OWNER=johnny"])


# ============================================================
# Group D: Move reverse / mixed source (2 cases)
# ============================================================

def group_d():
    print("\n[D] Move — reverse direction & mixed sources")
    t = hdr("johnny")
    sin = DOMAINS["johnny"]
    others = DOMAINS["user"]

    # D01: source in others, dest in sinopac (reverse of MT002-D)
    r = requests.patch(f"{API_URL}/api/files/move", headers=t,
                       json={"sourcePaths": [SETUP_FILES["user"]], "destinationPath": sin}, timeout=15)
    check_deny("MTX-D01", "D", "johnny move FROM others.com TO sinopac (source cross)", r)

    # D02: mixed sources — one own, one foreign; dest in own domain
    # first plant a movable file inside sinopac/tenantmtx via admin (to avoid side effects)
    r_pre = requests.post(f"{API_URL}/api/upload",
                          params={"path": f"{sin}/tenantmtx"}, headers=hdr("admin"),
                          files={"file": ("mover_own.txt", b"OWN", "text/plain")}, timeout=15)
    own_src = f"{sin}/tenantmtx/mover_own.txt"
    foreign_src = SETUP_FILES["user"]
    r = requests.patch(f"{API_URL}/api/files/move", headers=t,
                       json={"sourcePaths": [own_src, foreign_src],
                             "destinationPath": f"{sin}/tenantmtx"}, timeout=15)
    # Should 403 the whole request (all-or-nothing). Check the own_src was NOT moved/renamed.
    # MoveAsync in FileService loops; but Controller rejects whole batch. Expect 403.
    check_deny("MTX-D02", "D", "johnny mixed-source move (own + foreign)", r)
    # cleanup mover_own.txt
    requests.delete(f"{API_URL}/api/files", headers=hdr("admin"),
                    json={"paths": [own_src]}, timeout=15)


# ============================================================
# Group E: Rename cross-domain (2 cases)
# ============================================================

def group_e():
    print("\n[E] Rename cross-domain")
    t = hdr("johnny")
    # E01: rename a file in others.com
    r = requests.patch(f"{API_URL}/api/files/rename", headers=t,
                       json={"currentPath": SETUP_FILES["user"], "newName": "renamed_by_johnny.txt"}, timeout=15)
    check_deny("MTX-E01", "E", "johnny rename file in others.com", r)

    # E02: covered as A04 already; skip


# ============================================================
# Group F: Domain-root folder operations (3 cases)
# ============================================================

def group_f():
    print("\n[F] Operations on domain-root folders themselves")
    t = hdr("johnny")
    sin = DOMAINS["johnny"]

    # F01: rename sinopac.com folder
    r = requests.patch(f"{API_URL}/api/files/rename", headers=t,
                       json={"currentPath": sin, "newName": "sinopac_renamed"}, timeout=15)
    # sin IS within scope (equal to root). Rename will physically break the tenancy mapping.
    # Current code: IsWithinUserScope(sin) == True (fullPath == userRoot), so it would be allowed.
    # Expected-correct: 400/403 since user must not mutate their own root boundary.
    code = r.status_code
    if code in (400, 403):
        record("MTX-F01", "F", "johnny rename sinopac.com (own root)", "PASS", f"code={code}")
    else:
        record("MTX-F01", "F", "johnny rename sinopac.com (own root)",
               "FAIL", f"code={code} — user mutated domain-root boundary")
    # If it did rename, put it back
    if os.path.isdir(f"{ROOT}/sinopac_renamed") and not os.path.isdir(sin):
        os.rename(f"{ROOT}/sinopac_renamed", sin)

    # F02: delete sinopac.com folder
    r = requests.delete(f"{API_URL}/api/files", headers=t,
                        json={"paths": [sin]}, timeout=15)
    code = r.status_code
    # Expect 400/403. If 200 and folder gone, catastrophic.
    if code in (400, 403):
        record("MTX-F02", "F", "johnny delete sinopac.com (own root)", "PASS", f"code={code}")
    elif code == 200 and os.path.isdir(sin):
        # 200 but folder still exists — body.Success should be False
        try:
            j = r.json()
            ok = j.get("success") is False
            record("MTX-F02", "F", "johnny delete sinopac.com (own root)",
                   "PASS" if ok else "FAIL", f"code=200 body={j}")
        except Exception:
            record("MTX-F02", "F", "johnny delete sinopac.com (own root)",
                   "FAIL", "code=200 unparseable")
    else:
        record("MTX-F02", "F", "johnny delete sinopac.com (own root)",
               "FAIL", f"code={code} folder_gone={not os.path.isdir(sin)}")
    # If folder was actually deleted, recreate
    if not os.path.isdir(sin):
        os.makedirs(sin, exist_ok=True)

    # F03: move sinopac.com folder — try to move it to root (itself is src, dest is root)
    # destination ROOT is admin-only — as johnny, dest is NOT within scope → 403 expected
    r = requests.patch(f"{API_URL}/api/files/move", headers=t,
                       json={"sourcePaths": [sin], "destinationPath": ROOT}, timeout=15)
    check_deny("MTX-F03", "F", "johnny move sinopac.com folder to /data root", r)


# ============================================================
# Group G: Path normalization boundary (1 case)
# ============================================================

def group_g():
    print("\n[G] Path normalization boundary")
    t = hdr("johnny")
    # G01: /home/devpro/data/sinopac.com/../others.com  → resolves to others.com
    traversal = f"{DOMAINS['johnny']}/../others.com"
    r = requests.get(f"{API_URL}/api/files", params={"path": traversal}, headers=t, timeout=15)
    check_deny("MTX-G01", "G", "johnny traversal sinopac/../others",
               r, extra_forbidden=["marker_user"])


# ============================================================
# Group H: Admin sanity — can do everything everywhere (3 cases)
# ============================================================

def group_h():
    print("\n[H] Admin sanity across domains")
    a = hdr("admin")

    # H01: admin browse each domain
    all_ok = True
    for owner, droot in DOMAINS.items():
        r = requests.get(f"{API_URL}/api/files", params={"path": droot}, headers=a, timeout=15)
        if r.status_code != 200:
            all_ok = False; break
    record("MTX-H01", "H", "admin browse all 3 domains",
           "PASS" if all_ok else "FAIL", "all domains browsable")

    # H02: admin download sinopac marker
    r = requests.get(f"{API_URL}/api/files/download",
                     params={"path": SETUP_FILES["johnny"]}, headers=a, timeout=15)
    ok = r.status_code == 200 and "OWNER=johnny" in r.text
    record("MTX-H02", "H", "admin download sinopac marker",
           "PASS" if ok else "FAIL", f"code={r.status_code}")

    # H03: admin cross-domain move (sinopac marker → devpro/tenantmtx)
    # copy first via download+upload isn't trivial — do a true move then undo
    src = SETUP_FILES["johnny"]
    dest = f"{DOMAINS['admin']}/tenantmtx"
    r = requests.patch(f"{API_URL}/api/files/move", headers=a,
                       json={"sourcePaths": [src], "destinationPath": dest}, timeout=15)
    ok = r.status_code == 200
    record("MTX-H03", "H", "admin move sinopac → devpro",
           "PASS" if ok else "FAIL", f"code={r.status_code}")
    # move back
    requests.patch(f"{API_URL}/api/files/move", headers=a,
                   json={"sourcePaths": [f"{dest}/marker_johnny.txt"],
                         "destinationPath": f"{DOMAINS['johnny']}/tenantmtx"}, timeout=15)


# ============================================================
# Main
# ============================================================

def write_summary():
    ensure_dir(CASES_DIR)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    known  = sum(1 for r in results if r["status"] == "KNOWN")
    total  = len(results)

    lines = [
        f"# P003 v8 Tenant Matrix — {TEST_RUN}",
        "",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Scope:** Tenant-isolation matrix fills (Groups A/B/D/E/F/G/H)",
        f"**Total:** {total} | **PASS:** {passed} | **FAIL:** {failed} | **KNOWN:** {known}",
        "",
        "| Case | Group | Name | Status | Note |",
        "|------|-------|------|--------|------|",
    ]
    for r in results:
        lines.append(f"| {r['case']} | {r['group']} | {r['name']} | {r['status']} | {r['note']} |")

    with open(f"{CASES_DIR}/test_summary.md", "w") as f: f.write("\n".join(lines))
    with open(f"{CASES_DIR}/test_result_v8.json", "w") as f:
        json.dump({"test_run": TEST_RUN, "total": total, "pass": passed,
                   "fail": failed, "known": known, "cases": results},
                  f, indent=2, ensure_ascii=False)
    print(f"\n  Summary: {CASES_DIR}/test_summary.md")
    print(f"  JSON:    {CASES_DIR}/test_result_v8.json")
    return total, passed, failed, known


def main():
    print(f"P003 v8 Tenant Matrix — {TEST_RUN}")
    print("=" * 60)
    for k in ACCOUNTS:
        ok = login(k)
        print(f"  login {k}: {'OK' if ok else 'FAIL'}")
    if not all(k in tokens for k in ACCOUNTS):
        print("login incomplete, abort"); return

    try:
        setup_fixtures()
        group_a()
        group_b()
        group_d()
        group_e()
        group_f()
        group_g()
        group_h()
    finally:
        teardown_fixtures()

    total, passed, failed, known = write_summary()
    print("\n" + "=" * 60)
    print(f"  RESULT: {passed}/{total} PASS, {failed} FAIL, {known} KNOWN")
    print("=" * 60)


if __name__ == "__main__":
    main()
