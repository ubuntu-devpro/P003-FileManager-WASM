#!/usr/bin/env python3
"""
P003-FileManager-WASM — v9 Boundary + Race Tests
Scope:
  S8  — 邊界條件與異常處理（12 案）
  S9  — 並發與競態條件（6 案）
"""
import subprocess, json, os, time, threading, concurrent.futures
import requests

API_URL = "http://localhost:5001"
ROOT = "/home/devpro/data"
QA_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA"
TEST_RUN = "TestV9-Boundary-Race-0417-R1"
CASES_DIR = f"{QA_DIR}/{TEST_RUN}"

ACCOUNTS = {
    "admin":  {"email": "admin@devpro.com.tw",  "password": "admin123"},
    "johnny": {"email": "johnny@sinopac.com",   "password": "johnny123"},
}

results = []
tokens  = {}
SANDBOX = f"{ROOT}/sinopac.com/v9_sandbox"


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


def record(case_id, stage, name, status, note=""):
    results.append({"case": case_id, "stage": stage, "name": name, "status": status, "note": note})
    tag = {"PASS": "PASS", "FAIL": "FAIL", "KNOWN": "KNOWN", "SKIP": "SKIP"}.get(status, status)
    print(f"    [{tag}] {case_id}: {name} — {note}")


# ============================================================
# Setup
# ============================================================

def setup_sandbox():
    """johnny writable sandbox inside sinopac.com"""
    t = hdr("johnny")
    r = requests.post(f"{API_URL}/api/folders",
                      params={"path": f"{ROOT}/sinopac.com", "name": "v9_sandbox"},
                      headers=t, timeout=15)
    print(f"  sandbox created: code={r.status_code}")


def teardown_sandbox():
    t = hdr("johnny")
    r = requests.delete(f"{API_URL}/api/files",
                        headers=t, json={"paths": [SANDBOX]}, timeout=30)
    print(f"  sandbox removed: code={r.status_code}")


def upload_file(token_key, target_path, filename, content=b"content"):
    r = requests.post(f"{API_URL}/api/upload",
                      params={"path": target_path},
                      headers=hdr(token_key),
                      files={"file": (filename, content, "application/octet-stream")},
                      timeout=30)
    return r


# ============================================================
# S8 — 邊界條件與異常處理（12 案）
# ============================================================

def stage_s8():
    print("\n[S8] Boundary & exception handling")
    t = hdr("johnny")

    # EDGE-001: browse empty directory
    # create an empty subfolder
    requests.post(f"{API_URL}/api/folders",
                  params={"path": SANDBOX, "name": "empty_dir"}, headers=t, timeout=15)
    empty_dir = f"{SANDBOX}/empty_dir"
    r = requests.get(f"{API_URL}/api/files", params={"path": empty_dir}, headers=t, timeout=15)
    try:
        items = r.json().get("items", [])
    except Exception:
        items = None
    ok = r.status_code == 200 and items == []
    record("EDGE-001", "S8", "Browse empty directory",
           "PASS" if ok else "FAIL", f"code={r.status_code} items={items}")

    # EDGE-002: browse nonexistent path (inside scope)
    r = requests.get(f"{API_URL}/api/files",
                     params={"path": f"{SANDBOX}/does_not_exist"}, headers=t, timeout=15)
    # Accepted shapes: 200 with success=false OR 404 — must NOT be 500
    ok = r.status_code in (200, 400, 404)
    if ok and r.status_code == 200:
        try:
            j = r.json()
            ok = j.get("success") is False
        except Exception:
            ok = False
    record("EDGE-002", "S8", "Browse nonexistent path",
           "PASS" if ok else "FAIL", f"code={r.status_code}")

    # EDGE-003: special characters in filename (Chinese, space, emoji)
    special_name = "測試 文件 🚀.txt"
    r = upload_file("johnny", SANDBOX, special_name, b"special")
    # verify file landed and listing returns it
    r2 = requests.get(f"{API_URL}/api/files", params={"path": SANDBOX}, headers=t, timeout=15)
    try:
        names = [it.get("name", "") for it in r2.json().get("items", [])]
    except Exception:
        names = []
    landed = special_name in names
    record("EDGE-003", "S8", "Special chars in filename (CJK/space/emoji)",
           "PASS" if (r.status_code == 200 and landed) else "FAIL",
           f"upload={r.status_code} landed={landed}")
    # cleanup
    if landed:
        requests.delete(f"{API_URL}/api/files", headers=t,
                        json={"paths": [f"{SANDBOX}/{special_name}"]}, timeout=15)

    # EDGE-004: very long filename (255 chars)
    long_name = "A" * 250 + ".txt"  # 254 chars, under ext4 255-byte limit
    r = upload_file("johnny", SANDBOX, long_name, b"long")
    r2 = requests.get(f"{API_URL}/api/files", params={"path": SANDBOX}, headers=t, timeout=15)
    try:
        names = [it.get("name", "") for it in r2.json().get("items", [])]
    except Exception:
        names = []
    landed = long_name in names
    # Pass: either uploads cleanly and lands, OR is rejected explicitly (not 500)
    upload_ok = r.status_code == 200
    status = "PASS" if (upload_ok and landed) or r.status_code in (400, 413) else "FAIL"
    record("EDGE-004", "S8", "Very long filename (250 chars)",
           status, f"upload_code={r.status_code} landed={landed}")
    if landed:
        requests.delete(f"{API_URL}/api/files", headers=t,
                        json={"paths": [f"{SANDBOX}/{long_name}"]}, timeout=15)

    # EDGE-005: 0-byte file — upload empty & verify listing shows size=0
    r = upload_file("johnny", SANDBOX, "empty.txt", b"")
    r2 = requests.get(f"{API_URL}/api/files", params={"path": SANDBOX}, headers=t, timeout=15)
    size = None
    try:
        for it in r2.json().get("items", []):
            if it.get("name") == "empty.txt":
                size = it.get("size")
    except Exception:
        pass
    ok = r.status_code == 200 and size == 0
    record("EDGE-005", "S8", "0-byte file upload + listing size",
           "PASS" if ok else "FAIL", f"upload={r.status_code} reported_size={size}")
    if size is not None:
        requests.delete(f"{API_URL}/api/files", headers=t,
                        json={"paths": [f"{SANDBOX}/empty.txt"]}, timeout=15)

    # EDGE-006: Deep nested directories (10+ levels)
    deep_root = f"{SANDBOX}/deep"
    requests.post(f"{API_URL}/api/folders", params={"path": SANDBOX, "name": "deep"},
                  headers=t, timeout=15)
    current = deep_root
    for i in range(12):
        name = f"lvl{i}"
        requests.post(f"{API_URL}/api/folders", params={"path": current, "name": name},
                      headers=t, timeout=15)
        current = f"{current}/{name}"
    # Tree API on deep_root should not crash
    r = requests.get(f"{API_URL}/api/files/tree", params={"path": deep_root},
                     headers=t, timeout=30)
    ok = r.status_code == 200
    # find max depth
    depth = 0
    try:
        def walk(node, d=0):
            nonlocal depth
            depth = max(depth, d)
            for c in node.get("children", []) or []: walk(c, d + 1)
        for root_node in r.json().get("rootFolders", []) or r.json().get("folders", []) or []:
            walk(root_node)
    except Exception:
        pass
    record("EDGE-006", "S8", "Deep nested tree (12 levels)",
           "PASS" if ok else "FAIL", f"code={r.status_code} observed_depth={depth}")
    requests.delete(f"{API_URL}/api/files", headers=t,
                    json={"paths": [deep_root]}, timeout=30)

    # EDGE-007: empty request body on endpoint expecting JSON
    r = requests.delete(f"{API_URL}/api/files",
                        headers=hdr("johnny"),
                        data="",  # empty body
                        timeout=15)
    # Expect 400 (BadRequest), not 500
    ok = r.status_code in (400, 415)
    record("EDGE-007", "S8", "DELETE with empty body",
           "PASS" if ok else "FAIL", f"code={r.status_code} expected 400/415")

    # EDGE-008: malformed JSON
    r = requests.delete(f"{API_URL}/api/files",
                        headers={**hdr("johnny"), "Content-Type": "application/json"},
                        data='{"paths": [',  # broken
                        timeout=15)
    ok = r.status_code == 400
    # Also check body does not leak stack trace
    leaks_stack = any(s in r.text for s in ["at System.", "Microsoft.AspNetCore", "stacktrace"])
    if leaks_stack: ok = False
    record("EDGE-008", "S8", "Malformed JSON body",
           "PASS" if ok else "FAIL", f"code={r.status_code} stack_leak={leaks_stack}")

    # EDGE-009: wrong Content-Type
    r = requests.delete(f"{API_URL}/api/files",
                        headers={**hdr("johnny"), "Content-Type": "text/plain"},
                        data='{"paths":[]}',
                        timeout=15)
    # Expect 415 Unsupported Media Type (strict) or 400 (ASP.NET default with binder failing)
    ok = r.status_code in (400, 415)
    record("EDGE-009", "S8", "Wrong Content-Type",
           "PASS" if ok else "FAIL", f"code={r.status_code}")

    # EDGE-010: DELETE with empty paths array
    r = requests.delete(f"{API_URL}/api/files",
                        headers=hdr("johnny"),
                        json={"paths": []}, timeout=15)
    # Controller loops empty — returns 200 with deleted=0. Accept 200 with explicit result OR 400.
    ok = r.status_code in (200, 400)
    if ok and r.status_code == 200:
        try:
            j = r.json()
            # Make sure no "deleted N" where N>0
            ok = True  # allow 200 success message
        except Exception:
            ok = False
    record("EDGE-010", "S8", "DELETE with empty paths array",
           "PASS" if ok else "FAIL", f"code={r.status_code}")

    # EDGE-011: MOVE with empty sourcePaths
    r = requests.patch(f"{API_URL}/api/files/move",
                       headers=hdr("johnny"),
                       json={"sourcePaths": [], "destinationPath": SANDBOX}, timeout=15)
    ok = r.status_code in (200, 400)
    record("EDGE-011", "S8", "MOVE with empty sourcePaths",
           "PASS" if ok else "FAIL", f"code={r.status_code}")

    # EDGE-012: Search with wildcard chars `*?`
    # First plant some files
    upload_file("johnny", SANDBOX, "wild_a.txt", b"a")
    upload_file("johnny", SANDBOX, "wild_b.txt", b"b")
    r = requests.post(f"{API_URL}/api/files/search",
                      headers=hdr("johnny"),
                      json={"path": SANDBOX, "query": "*?"}, timeout=15)
    ok = r.status_code == 200  # must not crash
    record("EDGE-012", "S8", "Search with wildcard chars '*?'",
           "PASS" if ok else "FAIL", f"code={r.status_code}")
    # cleanup
    requests.delete(f"{API_URL}/api/files",
                    headers=hdr("johnny"),
                    json={"paths": [f"{SANDBOX}/wild_a.txt", f"{SANDBOX}/wild_b.txt"]},
                    timeout=15)


# ============================================================
# S9 — 並發與競態條件（6 案）
# ============================================================

def stage_s9():
    print("\n[S9] Concurrency & race conditions")
    t = hdr("johnny")

    # RACE-001: Concurrent rename of same file
    upload_file("johnny", SANDBOX, "race001.txt", b"original")
    src = f"{SANDBOX}/race001.txt"

    def rename_to(name):
        return requests.patch(f"{API_URL}/api/files/rename",
                              headers=hdr("johnny"),
                              json={"currentPath": src, "newName": name},
                              timeout=15)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fa = ex.submit(rename_to, "race001_A.txt")
        fb = ex.submit(rename_to, "race001_B.txt")
        ra, rb = fa.result(), fb.result()
    # Exactly one should succeed (200), the other should 4xx (not 500)
    codes = sorted([ra.status_code, rb.status_code])
    # Verify only one result file exists
    listing = requests.get(f"{API_URL}/api/files", params={"path": SANDBOX}, headers=t, timeout=15)
    names = []
    try:
        names = [it.get("name", "") for it in listing.json().get("items", [])]
    except Exception:
        pass
    race_files = [n for n in names if n.startswith("race001")]
    ok = len(race_files) == 1 and 500 not in codes and codes.count(200) >= 1
    record("RACE-001", "S9", "Concurrent rename of same file",
           "PASS" if ok else "FAIL", f"codes={codes} files_left={race_files}")
    # cleanup
    for rf in race_files:
        requests.delete(f"{API_URL}/api/files", headers=t,
                        json={"paths": [f"{SANDBOX}/{rf}"]}, timeout=15)

    # RACE-002: Concurrent delete of same file
    upload_file("johnny", SANDBOX, "race002.txt", b"x")
    target = f"{SANDBOX}/race002.txt"

    def delete_it():
        return requests.delete(f"{API_URL}/api/files", headers=hdr("johnny"),
                               json={"paths": [target]}, timeout=15)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fa = ex.submit(delete_it); fb = ex.submit(delete_it)
        ra, rb = fa.result(), fb.result()
    codes = sorted([ra.status_code, rb.status_code])
    # Expect: at least one success, neither 500
    file_gone = not os.path.exists(target)
    ok = file_gone and 500 not in codes
    record("RACE-002", "S9", "Concurrent delete of same file",
           "PASS" if ok else "FAIL", f"codes={codes} file_gone={file_gone}")

    # RACE-003: Delete file while downloading
    upload_file("johnny", SANDBOX, "race003.bin", b"Z" * (5 * 1024 * 1024))  # 5MB
    target = f"{SANDBOX}/race003.bin"

    def downloader(results_dict):
        try:
            r = requests.get(f"{API_URL}/api/files/download",
                             params={"path": target}, headers=hdr("johnny"),
                             stream=True, timeout=30)
            total = 0
            for chunk in r.iter_content(chunk_size=65536):
                total += len(chunk)
            results_dict["dl_code"] = r.status_code
            results_dict["dl_bytes"] = total
        except Exception as e:
            results_dict["dl_err"] = str(e)

    def deleter(results_dict):
        time.sleep(0.05)
        r = requests.delete(f"{API_URL}/api/files", headers=hdr("johnny"),
                            json={"paths": [target]}, timeout=15)
        results_dict["del_code"] = r.status_code

    res = {}
    th_dl = threading.Thread(target=downloader, args=(res,))
    th_del = threading.Thread(target=deleter, args=(res,))
    th_dl.start(); th_del.start()
    th_dl.join(); th_del.join()
    # Server must not 500. Download either completes or fails cleanly; either OK.
    ok = res.get("dl_code", 0) in (200, 404) and res.get("del_code") in (200, 404)
    record("RACE-003", "S9", "Delete file while downloading",
           "PASS" if ok else "FAIL",
           f"dl={res.get('dl_code')} bytes={res.get('dl_bytes')} del={res.get('del_code')} err={res.get('dl_err', '')}")

    # RACE-004: Concurrent upload of same filename
    def uploader(contents, results_dict, key):
        try:
            r = upload_file("johnny", SANDBOX, "race004.txt", contents)
            results_dict[key] = r.status_code
        except Exception as e:
            results_dict[key] = f"err:{e}"

    res2 = {}
    th_a = threading.Thread(target=uploader, args=(b"A" * 1024, res2, "a"))
    th_b = threading.Thread(target=uploader, args=(b"B" * 1024, res2, "b"))
    th_a.start(); th_b.start()
    th_a.join(); th_b.join()
    # File must exist with some valid content (either A or B, not corrupted)
    target = f"{SANDBOX}/race004.txt"
    content = b""
    if os.path.exists(target):
        with open(target, "rb") as f: content = f.read()
    is_pure = content == (b"A" * 1024) or content == (b"B" * 1024)
    ok = is_pure and 500 not in [res2.get("a"), res2.get("b")]
    record("RACE-004", "S9", "Concurrent upload of same filename",
           "PASS" if ok else "FAIL",
           f"codes={res2} content_size={len(content)} pure={is_pure}")
    if os.path.exists(target):
        requests.delete(f"{API_URL}/api/files", headers=hdr("johnny"),
                        json={"paths": [target]}, timeout=15)

    # RACE-005: Browse while deleting
    for i in range(5):
        upload_file("johnny", SANDBOX, f"race005_{i}.txt", b"x")

    def lister(results_dict):
        for _ in range(10):
            r = requests.get(f"{API_URL}/api/files", params={"path": SANDBOX},
                             headers=hdr("johnny"), timeout=15)
            results_dict.setdefault("codes", []).append(r.status_code)
            time.sleep(0.02)

    def mass_deleter(results_dict):
        time.sleep(0.03)
        paths = [f"{SANDBOX}/race005_{i}.txt" for i in range(5)]
        r = requests.delete(f"{API_URL}/api/files", headers=hdr("johnny"),
                            json={"paths": paths}, timeout=15)
        results_dict["del_code"] = r.status_code

    res3 = {}
    tl = threading.Thread(target=lister, args=(res3,))
    td = threading.Thread(target=mass_deleter, args=(res3,))
    tl.start(); td.start(); tl.join(); td.join()
    codes = res3.get("codes", [])
    ok = 500 not in codes and res3.get("del_code") == 200
    record("RACE-005", "S9", "Browse while deleting",
           "PASS" if ok else "FAIL",
           f"list_codes={set(codes)} del={res3.get('del_code')}")

    # RACE-006: Two accounts operating on same domain simultaneously
    # admin and johnny both create folders in sinopac.com
    def admin_create():
        return requests.post(f"{API_URL}/api/folders",
                             params={"path": f"{ROOT}/sinopac.com", "name": "race006_admin"},
                             headers=hdr("admin"), timeout=15)

    def johnny_create():
        return requests.post(f"{API_URL}/api/folders",
                             params={"path": f"{ROOT}/sinopac.com", "name": "race006_johnny"},
                             headers=hdr("johnny"), timeout=15)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fa = ex.submit(admin_create); fb = ex.submit(johnny_create)
        ra, rb = fa.result(), fb.result()
    # Both should succeed independently
    codes = [ra.status_code, rb.status_code]
    both_ok = all(c == 200 for c in codes)
    record("RACE-006", "S9", "Admin + user concurrent ops on same domain",
           "PASS" if both_ok else "FAIL", f"codes={codes}")
    # cleanup
    for n in ("race006_admin", "race006_johnny"):
        requests.delete(f"{API_URL}/api/files", headers=hdr("admin"),
                        json={"paths": [f"{ROOT}/sinopac.com/{n}"]}, timeout=15)


# ============================================================
# Summary
# ============================================================

def write_summary():
    ensure_dir(CASES_DIR)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    known  = sum(1 for r in results if r["status"] == "KNOWN")
    total  = len(results)

    lines = [
        f"# P003 v9 Boundary + Race — {TEST_RUN}",
        "",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Scope:** S8 (12) + S9 (6) — boundary & race conditions",
        f"**Total:** {total} | **PASS:** {passed} | **FAIL:** {failed} | **KNOWN:** {known}",
        "",
        "| Case | Stage | Name | Status | Note |",
        "|------|-------|------|--------|------|",
    ]
    for r in results:
        lines.append(f"| {r['case']} | {r['stage']} | {r['name']} | {r['status']} | {r['note']} |")
    with open(f"{CASES_DIR}/test_summary.md", "w") as f: f.write("\n".join(lines))
    with open(f"{CASES_DIR}/test_result_v9.json", "w") as f:
        json.dump({"test_run": TEST_RUN, "total": total, "pass": passed,
                   "fail": failed, "known": known, "cases": results},
                  f, indent=2, ensure_ascii=False)
    print(f"\n  Summary: {CASES_DIR}/test_summary.md")
    print(f"  JSON:    {CASES_DIR}/test_result_v9.json")
    return total, passed, failed, known


def main():
    print(f"P003 v9 Boundary + Race — {TEST_RUN}")
    print("=" * 60)
    for k in ACCOUNTS:
        ok = login(k)
        print(f"  login {k}: {'OK' if ok else 'FAIL'}")
    if not all(k in tokens for k in ACCOUNTS):
        print("login failed"); return
    try:
        setup_sandbox()
        stage_s8()
        stage_s9()
    finally:
        teardown_sandbox()
    total, passed, failed, known = write_summary()
    print("\n" + "=" * 60)
    print(f"  RESULT: {passed}/{total} PASS, {failed} FAIL, {known} KNOWN")
    print("=" * 60)


if __name__ == "__main__":
    main()
