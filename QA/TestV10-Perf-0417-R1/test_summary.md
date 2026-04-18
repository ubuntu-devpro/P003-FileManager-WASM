# P003 v10 Performance — TestV10-Perf-0417-R1

**Date:** 2026-04-17 23:10:01
**Scope:** S10 (5) — performance & stress
**Total:** 5 | **PASS:** 5 | **FAIL:** 0

| Case | Name | Status | Note |
|------|------|--------|------|
| PERF-001 | Browse 1000-file directory | PASS | code=200 items=1000 elapsed=15ms (threshold 3000ms) |
| PERF-002 | Upload 50 MB | PASS | code=200 landed=52.4MB elapsed=0.42s (threshold 30s) |
| PERF-003 | Download 200 MB streaming | PASS | code=200 bytes=209.7MB elapsed=0.29s server_rss_base=120MB peak=123MB growth=3MB |
| PERF-004 | Deep tree 60 levels | PASS | code=200 elapsed=0.01s (threshold 5s) |
| PERF-005 | 100 sequential GET calls | PASS | all_200=True elapsed=0.16s rss_base=123MB peak=128MB growth=5MB |