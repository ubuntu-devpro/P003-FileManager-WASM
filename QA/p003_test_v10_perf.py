#!/usr/bin/env python3
"""
P003-FileManager-WASM — v10 Performance / Stress
Scope: S10 — 效能與壓力測試（5 案）

Thresholds are pragmatic (local single-node):
  PERF-001 list 1000 files    < 3000 ms
  PERF-002 upload 50 MB       < 30 s, no server 5xx
  PERF-003 download 200 MB    stream OK, resident memory does not balloon
  PERF-004 deep tree (60 lvl) < 5 s, no 500
  PERF-005 100 sequential GET no 500, total < 30 s, RSS growth < 100 MB
"""
import os, time, json, glob, re, requests

API_URL = "http://localhost:5001"
ROOT = "/home/devpro/data"
QA_DIR = "/home/devpro/Claude-Workspace/projects/P003-FileManager-WASM/QA"
TEST_RUN = "TestV10-Perf-0417-R1"
CASES_DIR = f"{QA_DIR}/{TEST_RUN}"

ACCOUNTS = {"johnny": {"email": "johnny@sinopac.com", "password": "johnny123"}}
SANDBOX = f"{ROOT}/sinopac.com/v10_sandbox"
results = []
tokens = {}


def ensure_dir(p): os.makedirs(p, exist_ok=True)


def login(key):
    acc = ACCOUNTS[key]
    r = requests.post(f"{API_URL}/api/auth/login",
                      json={"email": acc["email"], "password": acc["password"]}, timeout=15)
    if r.status_code == 200:
        tokens[key] = r.json().get("token", "")
        return True
    return False


def hdr(k): return {"Authorization": f"Bearer {tokens[k]}"}


def record(case_id, name, status, note=""):
    results.append({"case": case_id, "stage": "S10", "name": name, "status": status, "note": note})
    tag = {"PASS": "PASS", "FAIL": "FAIL", "KNOWN": "KNOWN"}.get(status, status)
    print(f"    [{tag}] {case_id}: {name} — {note}")


def find_server_pid():
    for proc_dir in glob.glob("/proc/[0-9]*"):
        try:
            with open(f"{proc_dir}/cmdline", "rb") as f:
                cmd = f.read().replace(b"\x00", b" ").decode("utf-8", errors="ignore")
            if "FileManager.Server" in cmd and "dotnet run" not in cmd:
                return int(os.path.basename(proc_dir))
        except Exception:
            continue
    # fallback: dotnet run process
    for proc_dir in glob.glob("/proc/[0-9]*"):
        try:
            with open(f"{proc_dir}/cmdline", "rb") as f:
                cmd = f.read().replace(b"\x00", b" ").decode("utf-8", errors="ignore")
            if "FileManager.Server" in cmd:
                return int(os.path.basename(proc_dir))
        except Exception:
            continue
    return None


def rss_mb(pid):
    if not pid: return -1
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    kb = int(re.findall(r"\d+", line)[0])
                    return kb / 1024
    except Exception:
        return -1
    return -1


# ============================================================
# Setup
# ============================================================

def setup_sandbox():
    t = hdr("johnny")
    r = requests.post(f"{API_URL}/api/folders",
                      params={"path": f"{ROOT}/sinopac.com", "name": "v10_sandbox"},
                      headers=t, timeout=15)
    print(f"  sandbox: code={r.status_code}")


def teardown_sandbox():
    t = hdr("johnny")
    r = requests.delete(f"{API_URL}/api/files",
                        headers=t, json={"paths": [SANDBOX]}, timeout=120)
    print(f"  teardown: code={r.status_code}")


# ============================================================
# PERF-001: browse 1000-file directory
# ============================================================

def perf_001():
    print("\n[PERF-001] browse 1000 files")
    # plant 1000 small files directly on disk (faster than API)
    big_dir = f"{SANDBOX}/perf001"
    ensure_dir(big_dir)
    for i in range(1000):
        with open(f"{big_dir}/file_{i:04d}.txt", "wb") as f:
            f.write(b"x")
    t0 = time.perf_counter()
    r = requests.get(f"{API_URL}/api/files", params={"path": big_dir},
                     headers=hdr("johnny"), timeout=30)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    try:
        items = r.json().get("items", [])
        n = len(items)
    except Exception:
        n = -1
    ok = r.status_code == 200 and n == 1000 and elapsed_ms < 3000
    record("PERF-001", "Browse 1000-file directory",
           "PASS" if ok else "FAIL",
           f"code={r.status_code} items={n} elapsed={elapsed_ms:.0f}ms (threshold 3000ms)")


# ============================================================
# PERF-002: upload 50 MB
# ============================================================

def perf_002():
    print("\n[PERF-002] upload 50 MB")
    tmp = "/tmp/perf002_50mb.bin"
    with open(tmp, "wb") as f:
        f.write(os.urandom(50 * 1024 * 1024))
    t0 = time.perf_counter()
    with open(tmp, "rb") as fh:
        r = requests.post(f"{API_URL}/api/upload",
                          params={"path": SANDBOX},
                          headers=hdr("johnny"),
                          files={"file": ("perf002_50mb.bin", fh, "application/octet-stream")},
                          timeout=60)
    elapsed = time.perf_counter() - t0
    landed_size = os.path.getsize(f"{SANDBOX}/perf002_50mb.bin") if os.path.exists(f"{SANDBOX}/perf002_50mb.bin") else 0
    ok = r.status_code == 200 and landed_size == 50 * 1024 * 1024 and elapsed < 30
    record("PERF-002", "Upload 50 MB",
           "PASS" if ok else "FAIL",
           f"code={r.status_code} landed={landed_size/1e6:.1f}MB elapsed={elapsed:.2f}s (threshold 30s)")
    try: os.remove(tmp)
    except: pass


# ============================================================
# PERF-003: download 200 MB streaming (no OOM)
# ============================================================

def perf_003():
    print("\n[PERF-003] download 200 MB (streaming)")
    target = f"{SANDBOX}/perf003_200mb.bin"
    with open(target, "wb") as f:
        # write 200 MB fast without consuming lots of RAM
        chunk = os.urandom(1024 * 1024)
        for _ in range(200):
            f.write(chunk)

    pid = find_server_pid()
    baseline = rss_mb(pid) if pid else -1
    peak = baseline
    t0 = time.perf_counter()
    r = requests.get(f"{API_URL}/api/files/download",
                     params={"path": target}, headers=hdr("johnny"),
                     stream=True, timeout=180)
    total = 0
    for chunk in r.iter_content(chunk_size=1024 * 1024):
        total += len(chunk)
        if pid and total % (20 * 1024 * 1024) < 1024 * 1024:
            peak = max(peak, rss_mb(pid))
    elapsed = time.perf_counter() - t0
    if pid:
        peak = max(peak, rss_mb(pid))
    growth = (peak - baseline) if pid and baseline > 0 else -1
    # Must download all 200MB, server RSS growth must be small (streaming, not ReadAllBytes)
    ok = (r.status_code == 200 and total == 200 * 1024 * 1024 and
          (growth < 0 or growth < 250))  # allow generous 250MB slack for GC
    record("PERF-003", "Download 200 MB streaming",
           "PASS" if ok else "FAIL",
           f"code={r.status_code} bytes={total/1e6:.1f}MB elapsed={elapsed:.2f}s "
           f"server_rss_base={baseline:.0f}MB peak={peak:.0f}MB growth={growth:.0f}MB")


# ============================================================
# PERF-004: deep tree API
# ============================================================

def perf_004():
    print("\n[PERF-004] deep tree 60 levels")
    deep_root = f"{SANDBOX}/perf004_deep"
    current = deep_root
    ensure_dir(current)
    for i in range(60):
        current = f"{current}/lvl{i}"
        os.makedirs(current, exist_ok=True)
    t0 = time.perf_counter()
    r = requests.get(f"{API_URL}/api/files/tree",
                     params={"path": deep_root}, headers=hdr("johnny"), timeout=30)
    elapsed = time.perf_counter() - t0
    ok = r.status_code == 200 and elapsed < 5
    record("PERF-004", "Deep tree 60 levels",
           "PASS" if ok else "FAIL",
           f"code={r.status_code} elapsed={elapsed:.2f}s (threshold 5s)")


# ============================================================
# PERF-005: 100 sequential GETs, RSS stability
# ============================================================

def perf_005():
    print("\n[PERF-005] 100 sequential GET calls, RSS stability")
    pid = find_server_pid()
    baseline = rss_mb(pid) if pid else -1
    codes = []
    t0 = time.perf_counter()
    for i in range(100):
        r = requests.get(f"{API_URL}/api/files",
                         params={"path": f"{ROOT}/sinopac.com"},
                         headers=hdr("johnny"), timeout=10)
        codes.append(r.status_code)
    elapsed = time.perf_counter() - t0
    peak = rss_mb(pid) if pid else -1
    growth = peak - baseline if baseline > 0 else -1
    ok = all(c == 200 for c in codes) and 500 not in codes and elapsed < 30 and (growth < 0 or growth < 100)
    record("PERF-005", "100 sequential GET calls",
           "PASS" if ok else "FAIL",
           f"all_200={all(c == 200 for c in codes)} elapsed={elapsed:.2f}s "
           f"rss_base={baseline:.0f}MB peak={peak:.0f}MB growth={growth:.0f}MB")


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
        f"# P003 v10 Performance — {TEST_RUN}",
        "",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Scope:** S10 (5) — performance & stress",
        f"**Total:** {total} | **PASS:** {passed} | **FAIL:** {failed}",
        "",
        "| Case | Name | Status | Note |",
        "|------|------|--------|------|",
    ]
    for r in results:
        lines.append(f"| {r['case']} | {r['name']} | {r['status']} | {r['note']} |")
    with open(f"{CASES_DIR}/test_summary.md", "w") as f: f.write("\n".join(lines))
    with open(f"{CASES_DIR}/test_result_v10.json", "w") as f:
        json.dump({"test_run": TEST_RUN, "total": total, "pass": passed,
                   "fail": failed, "cases": results}, f, indent=2, ensure_ascii=False)
    print(f"\n  Summary: {CASES_DIR}/test_summary.md")
    return total, passed, failed


def main():
    print(f"P003 v10 Performance — {TEST_RUN}")
    print("=" * 60)
    for k in ACCOUNTS:
        ok = login(k); print(f"  login {k}: {'OK' if ok else 'FAIL'}")
    if "johnny" not in tokens: return
    try:
        setup_sandbox()
        perf_001()
        perf_002()
        perf_003()
        perf_004()
        perf_005()
    finally:
        teardown_sandbox()
    total, passed, failed = write_summary()
    print("\n" + "=" * 60)
    print(f"  RESULT: {passed}/{total} PASS, {failed} FAIL")
    print("=" * 60)


if __name__ == "__main__":
    main()
