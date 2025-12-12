# Chaos Lock Performance Results Dataset

This folder contains **appendable, machine-readable performance measurements** intended for use in a white paper.

## Files

- `perf_results.csv`
  - Spreadsheet-friendly dataset (one row per run).
- `perf_results.jsonl`
  - JSON Lines dataset (one JSON object per run). Best for programmatic analysis.
- `parse_perf_log.py`
  - Parser for existing console logs (e.g., `Test-logs/encryption-ex1.md`) that appends results to both datasets.

## Schema (common fields)

- `run_id`
  - Unique identifier for the run (defaults to log filename stem).
- `date_utc`
  - ISO-8601 timestamp (UTC). If missing from the log, parser uses file mtime.
- `test_name`
  - Human-readable test label.
- `implementation`
  - Which implementation produced the log (e.g., `Python Easy Encryption V2`, SwiftUI).
- `dataset_path`
  - Folder used for the run (from `🔒 Locking folder:` line when present).
- `total_files`
  - Total file count.
- `total_size_mb`
  - Total size in MB (from progress accounting lines).
- `total_time_s`
  - Total runtime in seconds (from `⏱️  Total time:`).
- `throughput_mb_s`
  - Computed: `total_size_mb / total_time_s`.
- `files_per_s`
  - Computed: `total_files / total_time_s`.
- `pbkdf2_iterations`
  - PBKDF2 iteration count (parsed from lines like `(100k iterations)` or `(250000 iterations)`).
- `aes_mode`
  - Encryption mode (e.g., `AES-256-GCM`).
- `machine.os_version`, `machine.cpu`, `machine.ram_bytes`, `machine.disk_root_free_human`
  - System context captured at parse time.

## How to append a new run

If you have a new log in the same style as `Test-logs/encryption-ex1.md`:

```bash
python3 performance_results/parse_perf_log.py Test-logs/<your_log>.md \
  --csv performance_results/perf_results.csv \
  --jsonl performance_results/perf_results.jsonl
```

## Notes on measurement quality

Some logs may show a **size-progress mismatch** near completion (e.g., `processed/total MB` not reaching 100% even though the run completes). The dataset stores the reported `total_size_mb` and `total_time_s` but preserves a warning in `notes` to avoid overstating precision.
