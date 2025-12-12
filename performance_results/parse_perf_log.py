#!/usr/bin/env python3

import argparse
import csv
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class MachineInfo:
    os_version: str
    cpu: str
    ram_bytes: int
    disk_root_free_human: str


@dataclass
class PerfResult:
    run_id: str
    date_utc: Optional[str]
    test_name: str
    implementation: str
    dataset_path: Optional[str]
    total_files: int
    total_size_mb: float
    total_time_s: float
    throughput_mb_s: float
    files_per_s: float
    pbkdf2_iterations: Optional[int]
    aes_mode: Optional[str]
    notes: str
    machine: MachineInfo


def _cmd(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        out = (r.stdout or r.stderr or "").strip()
        return out
    except Exception:
        return ""


def get_machine_info() -> MachineInfo:
    cpu = _cmd(["sysctl", "-n", "machdep.cpu.brand_string"]) or _cmd(["sysctl", "-n", "hw.model"]) or "unknown"

    ram_str = _cmd(["sysctl", "-n", "hw.memsize"]) or "0"
    try:
        ram_bytes = int(ram_str)
    except ValueError:
        ram_bytes = 0

    os_version = _cmd(["sw_vers"]) or "unknown"
    os_version = os_version.replace("\n", " | ")

    df_line = _cmd(["df", "-h", "/"])
    disk_root_free_human = "unknown"
    # Expect last line to include SIZE USED AVAIL
    lines = df_line.splitlines()
    if len(lines) >= 2:
        parts = lines[-1].split()
        # filesystem size used avail ... mount
        if len(parts) >= 4:
            disk_root_free_human = f"{parts[3]} free of {parts[1]}"

    return MachineInfo(
        os_version=os_version,
        cpu=cpu,
        ram_bytes=ram_bytes,
        disk_root_free_human=disk_root_free_human,
    )


def parse_log(log_path: Path) -> PerfResult:
    text = log_path.read_text(errors="ignore")

    dataset_path = None
    m = re.search(r"^🔒 Locking folder:\s*(.+)$", text, re.MULTILINE)
    if m:
        dataset_path = m.group(1).strip()

    pbkdf2_iterations = None
    # Common formats observed in logs:
    # - "... (100k iterations)"
    # - "... (250000 iterations)"
    # - "PBKDF2 ... (100k iterations)"
    m = re.search(r"\((\d+)\s*k\s*iterations\)", text, re.IGNORECASE)
    if m:
        pbkdf2_iterations = int(m.group(1)) * 1000
    else:
        m = re.search(r"\((\d{4,})\s*iterations\)", text, re.IGNORECASE)
        if m:
            pbkdf2_iterations = int(m.group(1))

    aes_mode = None
    if re.search(r"AES-256-GCM", text, re.IGNORECASE):
        aes_mode = "AES-256-GCM"

    total_files = None
    total_size_mb = None
    last_progress = None
    for line in text.splitlines():
        if "📦" in line and "/" in line and "MB" in line:
            last_progress = line

    if last_progress:
        # Example: 📦 15299/15397 files (99%) | 5629.5/11363.8 MB (49%) | ETA: 398s
        m = re.search(r"\b(\d+)\s*/\s*(\d+)\s*files\b", last_progress)
        if m:
            total_files = int(m.group(2))
        m = re.search(r"\b([0-9.]+)\s*/\s*([0-9.]+)\s*MB\b", last_progress)
        if m:
            total_size_mb = float(m.group(2))

    if total_files is None or total_size_mb is None:
        raise SystemExit(f"Could not parse total files/size from progress lines in {log_path}")

    total_time_s = None
    m = re.search(r"Total time:\s*([0-9.]+)s", text)
    if m:
        total_time_s = float(m.group(1))
    if total_time_s is None:
        raise SystemExit(f"Could not parse total time from {log_path} (expected 'Total time: <s>s')")

    throughput_mb_s = (total_size_mb / total_time_s) if total_time_s > 0 else 0.0
    files_per_s = (total_files / total_time_s) if total_time_s > 0 else 0.0

    # Use file mtime as run timestamp if available
    try:
        dt = datetime.fromtimestamp(log_path.stat().st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        dt = None

    run_id = log_path.stem

    notes = ""
    if "✅ Folder locked successfully" in text:
        notes += "Log includes completion marker. "
    # Flag size counter mismatch if present
    if re.search(r"\b([0-9.]+)\s*/\s*([0-9.]+)\s*MB\s*\(49%\)", text):
        notes += "Progress size counter shows ~49% at end; treat as accounting artifact (batching/size counter mismatch). "

    machine = get_machine_info()

    return PerfResult(
        run_id=run_id,
        date_utc=dt,
        test_name="Folder Lock Stress Test",
        implementation="Python Easy Encryption V2",
        dataset_path=dataset_path,
        total_files=total_files,
        total_size_mb=total_size_mb,
        total_time_s=total_time_s,
        throughput_mb_s=round(throughput_mb_s, 2),
        files_per_s=round(files_per_s, 2),
        pbkdf2_iterations=pbkdf2_iterations,
        aes_mode=aes_mode,
        notes=notes.strip(),
        machine=machine,
    )


def append_csv(csv_path: Path, r: PerfResult) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    header = [
        "run_id",
        "date_utc",
        "test_name",
        "implementation",
        "dataset_path",
        "total_files",
        "total_size_mb",
        "total_time_s",
        "throughput_mb_s",
        "files_per_s",
        "pbkdf2_iterations",
        "aes_mode",
        "notes",
        "os_version",
        "cpu",
        "ram_bytes",
        "disk_root_free_human",
    ]

    row = {
        "run_id": r.run_id,
        "date_utc": r.date_utc or "",
        "test_name": r.test_name,
        "implementation": r.implementation,
        "dataset_path": r.dataset_path or "",
        "total_files": r.total_files,
        "total_size_mb": r.total_size_mb,
        "total_time_s": r.total_time_s,
        "throughput_mb_s": r.throughput_mb_s,
        "files_per_s": r.files_per_s,
        "pbkdf2_iterations": r.pbkdf2_iterations or "",
        "aes_mode": r.aes_mode or "",
        "notes": r.notes,
        "os_version": r.machine.os_version,
        "cpu": r.machine.cpu,
        "ram_bytes": r.machine.ram_bytes,
        "disk_root_free_human": r.machine.disk_root_free_human,
    }

    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if write_header:
            w.writeheader()
        w.writerow(row)


def append_jsonl(jsonl_path: Path, r: PerfResult) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(r)
    with jsonl_path.open("a") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", type=Path)
    ap.add_argument("--csv", type=Path, default=Path("performance_results/perf_results.csv"))
    ap.add_argument("--jsonl", type=Path, default=Path("performance_results/perf_results.jsonl"))
    args = ap.parse_args()

    r = parse_log(args.log)
    append_csv(args.csv, r)
    append_jsonl(args.jsonl, r)

    print(json.dumps(asdict(r), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
