#!/usr/bin/env python
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
from email.message import EmailMessage
from pathlib import Path
import smtplib
import socket
import sys
from typing import Dict, Iterable, List, Tuple


DEFAULT_ENV_PATH = Path("automation") / "daily_change_report.env"
DEFAULT_STATE_DIR = Path(".codex-automation") / "daily-change-report"
DEFAULT_EXCLUDES = [
    ".codex-automation/**",
    ".git/**",
    ".git",
    "__pycache__/**",
    "node_modules/**",
]


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def parse_patterns(value: str) -> List[str]:
    if not value:
        return []
    patterns: List[str] = []
    for chunk in value.replace(";", "\n").splitlines():
        for part in chunk.split(","):
            item = part.strip().replace("\\", "/")
            if item:
                patterns.append(item)
    return patterns


def normalize_relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matches_pattern(relpath: str, pattern: str) -> bool:
    if fnmatch.fnmatch(relpath, pattern):
        return True
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return relpath == prefix or relpath.startswith(prefix + "/")
    return relpath == pattern.rstrip("/")


def should_exclude(relpath: str, patterns: Iterable[str]) -> bool:
    return any(matches_pattern(relpath, pattern) for pattern in patterns)


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_workspace(
    root: Path,
    previous_snapshot: Dict[str, dict],
    exclude_patterns: List[str],
) -> Tuple[Dict[str, dict], List[str]]:
    snapshot: Dict[str, dict] = {}
    skipped: List[str] = []

    for current_root, dirnames, filenames in os.walk(root):
        current_root_path = Path(current_root)
        rel_root = "." if current_root_path == root else normalize_relpath(current_root_path, root)

        kept_dirs = []
        for dirname in dirnames:
            child_rel = dirname if rel_root == "." else f"{rel_root}/{dirname}"
            if should_exclude(child_rel, exclude_patterns):
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            file_path = current_root_path / filename
            relpath = normalize_relpath(file_path, root)
            if should_exclude(relpath, exclude_patterns):
                continue

            try:
                stat = file_path.stat()
                previous = previous_snapshot.get(relpath)
                if (
                    previous
                    and previous.get("size") == stat.st_size
                    and previous.get("mtime_ns") == stat.st_mtime_ns
                ):
                    file_hash = previous.get("sha256", "")
                else:
                    file_hash = sha256_for_file(file_path)

                snapshot[relpath] = {
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                    "modified_at": dt.datetime.fromtimestamp(
                        stat.st_mtime, dt.timezone.utc
                    ).isoformat(),
                    "sha256": file_hash,
                }
            except (OSError, PermissionError) as exc:
                skipped.append(f"{relpath}: {exc}")

    return snapshot, skipped


def compare_snapshots(
    old_snapshot: Dict[str, dict],
    new_snapshot: Dict[str, dict],
) -> Tuple[List[str], List[str], List[str]]:
    old_paths = set(old_snapshot)
    new_paths = set(new_snapshot)

    added = sorted(new_paths - old_paths)
    deleted = sorted(old_paths - new_paths)
    modified = sorted(
        path
        for path in (old_paths & new_paths)
        if old_snapshot[path].get("sha256") != new_snapshot[path].get("sha256")
    )
    return added, modified, deleted


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f}{unit}" if unit != "B" else f"{int(value)}B"
        value /= 1024
    return f"{size}B"


def summarize_group(title: str, items: List[str], snapshot: Dict[str, dict], max_items: int) -> List[str]:
    lines = [f"{title}: {len(items)}"]
    for relpath in items[:max_items]:
        details = snapshot.get(relpath)
        if details:
            lines.append(
                f"  - {relpath} | {format_bytes(int(details.get('size', 0)))} | {details.get('modified_at', '')}"
            )
        else:
            lines.append(f"  - {relpath}")

    hidden_count = max(0, len(items) - max_items)
    if hidden_count:
        lines.append(f"  - ... and {hidden_count} more")
    return lines


def build_report(
    *,
    root: Path,
    report_name: str,
    window_start: str,
    window_end: str,
    added: List[str],
    modified: List[str],
    deleted: List[str],
    snapshot: Dict[str, dict],
    skipped: List[str],
    max_items: int,
) -> str:
    host = socket.gethostname()
    total_changes = len(added) + len(modified) + len(deleted)

    lines = [
        f"{report_name}",
        "",
        f"Folder: {root}",
        f"Machine: {host}",
        f"Window start: {window_start}",
        f"Window end:   {window_end}",
        f"Total changes: {total_changes}",
        "",
    ]

    lines.extend(summarize_group("Added files", added, snapshot, max_items))
    lines.append("")
    lines.extend(summarize_group("Modified files", modified, snapshot, max_items))
    lines.append("")
    lines.extend(summarize_group("Deleted files", deleted, snapshot, max_items))

    if skipped:
        lines.append("")
        lines.append(f"Skipped files: {len(skipped)}")
        for item in skipped[:max_items]:
            lines.append(f"  - {item}")
        hidden_count = max(0, len(skipped) - max_items)
        if hidden_count:
            lines.append(f"  - ... and {hidden_count} more")

    if total_changes == 0:
        lines.append("")
        lines.append("No file content changes were detected in this window.")

    return "\n".join(lines) + "\n"


def send_email(subject: str, body: str, smtp_config: Dict[str, str]) -> None:
    message = EmailMessage()
    message["From"] = smtp_config["from_addr"]
    message["To"] = smtp_config["to_addr"]
    message["Subject"] = subject
    message.set_content(body)

    host = smtp_config["host"]
    port = int(smtp_config["port"])
    username = smtp_config["username"]
    password = smtp_config["password"]
    use_ssl = smtp_config["use_ssl"].lower() in {"1", "true", "yes", "on"}
    use_starttls = smtp_config["use_starttls"].lower() in {"1", "true", "yes", "on"}

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, timeout=30) as server:
            server.login(username, password)
            server.send_message(message)
        return

    with smtplib.SMTP(host, port, timeout=30) as server:
        if use_starttls:
            server.starttls()
        server.login(username, password)
        server.send_message(message)


def load_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(state_path: Path, payload: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a file-change report for a folder and send it by email."
    )
    parser.add_argument("--root", default=".", help="Folder to scan.")
    parser.add_argument("--recipient", default="", help="Email recipient override.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH), help="Path to the report env file.")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="State directory for snapshots and reports.")
    parser.add_argument("--report-name", default="Daily Folder Change Report", help="Report title.")
    parser.add_argument("--max-items", type=int, default=200, help="Max entries shown per section.")
    parser.add_argument(
        "--allow-empty-recipient",
        action="store_true",
        help="Do not fail if the recipient is missing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (root / env_path).resolve()
    load_env_file(env_path)

    state_dir = Path(args.state_dir)
    if not state_dir.is_absolute():
        state_dir = (root / state_dir).resolve()
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / "state.json"
    reports_dir = state_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    exclude_patterns = DEFAULT_EXCLUDES + parse_patterns(get_env("REPORT_EXCLUDE_PATTERNS"))
    smtp_to = args.recipient.strip() or get_env("REPORT_SMTP_TO")
    smtp_config = {
        "host": get_env("REPORT_SMTP_HOST", "smtp.qq.com"),
        "port": get_env("REPORT_SMTP_PORT", "465"),
        "username": get_env("REPORT_SMTP_USER"),
        "password": get_env("REPORT_SMTP_PASSWORD"),
        "from_addr": get_env("REPORT_SMTP_FROM") or get_env("REPORT_SMTP_USER"),
        "to_addr": smtp_to,
        "use_ssl": get_env("REPORT_SMTP_USE_SSL", "true"),
        "use_starttls": get_env("REPORT_SMTP_USE_STARTTLS", "false"),
    }

    state = load_state(state_path)
    previous_snapshot = state.get("snapshot", {})
    previous_window_end = state.get("window_end")
    now = dt.datetime.now().astimezone()
    window_end = now.isoformat()

    snapshot, skipped = scan_workspace(root, previous_snapshot, exclude_patterns)

    if not previous_snapshot:
        initial_state = {
            "root": str(root),
            "window_start": window_end,
            "window_end": window_end,
            "snapshot": snapshot,
            "initialized_at": now.isoformat(),
        }
        save_state(state_path, initial_state)

        baseline_report = (
            f"{args.report_name}\n\n"
            f"Folder: {root}\n"
            f"Baseline created at: {window_end}\n\n"
            "The first snapshot has been stored successfully. "
            "The next scheduled run will compare changes against this baseline.\n"
        )
        baseline_file = reports_dir / f"{now.strftime('%Y%m%d_%H%M%S')}_baseline.txt"
        baseline_file.write_text(baseline_report, encoding="utf-8")

        if smtp_config["to_addr"] and smtp_config["username"] and smtp_config["password"]:
            subject = f"{get_env('REPORT_SUBJECT_PREFIX', '[Folder Report]')} Baseline created"
            send_email(subject, baseline_report, smtp_config)
            print("Baseline created and emailed.")
        else:
            print("Baseline created. Email not sent because SMTP settings are incomplete.")
        return 0

    added, modified, deleted = compare_snapshots(previous_snapshot, snapshot)
    window_start = previous_window_end or state.get("window_start") or "unknown"
    report_body = build_report(
        root=root,
        report_name=args.report_name,
        window_start=window_start,
        window_end=window_end,
        added=added,
        modified=modified,
        deleted=deleted,
        snapshot=snapshot,
        skipped=skipped,
        max_items=max(1, args.max_items),
    )
    report_file = reports_dir / f"{now.strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.write_text(report_body, encoding="utf-8")

    if not smtp_config["to_addr"] and not args.allow_empty_recipient:
        print("Recipient email is missing. Set REPORT_SMTP_TO or use --recipient.", file=sys.stderr)
        return 2
    if not smtp_config["username"] or not smtp_config["password"] or not smtp_config["from_addr"]:
        print(
            "SMTP settings are incomplete. Please set REPORT_SMTP_USER, REPORT_SMTP_PASSWORD, and REPORT_SMTP_FROM.",
            file=sys.stderr,
        )
        return 3

    subject_prefix = get_env("REPORT_SUBJECT_PREFIX", "[Folder Report]")
    subject = f"{subject_prefix} {window_start} -> {window_end}"

    try:
        send_email(subject, report_body, smtp_config)
    except Exception as exc:  # pragma: no cover - best effort for runtime diagnostics
        print(f"Failed to send email: {exc}", file=sys.stderr)
        return 4

    next_state = {
        "root": str(root),
        "window_start": window_start,
        "window_end": window_end,
        "snapshot": snapshot,
        "last_report_file": str(report_file),
        "last_sent_at": dt.datetime.now().astimezone().isoformat(),
    }
    save_state(state_path, next_state)
    print(f"Report sent successfully to {smtp_config['to_addr']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
