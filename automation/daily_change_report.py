#!/usr/bin/env python
import argparse
import datetime as dt
from email.message import EmailMessage
import os
from pathlib import Path
import smtplib
import socket
import subprocess
import sys
from typing import Dict, List, Tuple


DEFAULT_ENV_PATH = Path("automation") / "daily_change_report.env"
DEFAULT_STATE_DIR = Path(".codex-automation") / "daily-change-report"


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


def run_git(repo_root: Path, args: List[str]) -> str:
    command = ["git", *args]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout


def ensure_git_repo(repo_root: Path) -> None:
    run_git(repo_root, ["rev-parse", "--show-toplevel"])


def resolve_window(
    *,
    now: dt.datetime,
    scheduled_hour: int,
    since: str,
    until: str,
    day_offset: int,
) -> Tuple[dt.datetime, dt.datetime]:
    if since or until:
        if not (since and until):
            raise ValueError("Both --since and --until must be provided together.")
        return (
            dt.datetime.fromisoformat(since).astimezone(),
            dt.datetime.fromisoformat(until).astimezone(),
        )

    today_anchor = now.replace(hour=scheduled_hour, minute=0, second=0, microsecond=0)
    latest_window_end = today_anchor if now >= today_anchor else today_anchor - dt.timedelta(days=1)
    window_end = latest_window_end - dt.timedelta(days=day_offset)
    window_start = window_end - dt.timedelta(days=1)
    return window_start, window_end


def parse_log_output(raw_output: str) -> List[dict]:
    commits: List[dict] = []
    current: dict | None = None
    header_keys = ["hash", "short_hash", "author", "author_email", "date", "subject"]
    pending_header_index = -1

    for raw_line in raw_output.splitlines():
        line = raw_line.rstrip("\n")
        if line == "@@COMMIT@@":
            if current:
                commits.append(current)
            current = {"files": [], "insertions": 0, "deletions": 0}
            pending_header_index = 0
            continue

        if current is None:
            continue

        if 0 <= pending_header_index < len(header_keys):
            current[header_keys[pending_header_index]] = line
            pending_header_index += 1
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        added_raw, deleted_raw, path = parts
        added = 0 if added_raw == "-" else int(added_raw)
        deleted = 0 if deleted_raw == "-" else int(deleted_raw)
        current["insertions"] += added
        current["deletions"] += deleted
        current["files"].append(
            {
                "path": path,
                "insertions": added,
                "deletions": deleted,
                "binary": added_raw == "-" or deleted_raw == "-",
            }
        )

    if current:
        commits.append(current)
    return commits


def get_commits(repo_root: Path, since_iso: str, until_iso: str) -> List[dict]:
    output = run_git(
        repo_root,
        [
            "log",
            f"--since={since_iso}",
            f"--until={until_iso}",
            "--date=iso-local",
            "--pretty=format:@@COMMIT@@%n%H%n%h%n%an%n%ae%n%ad%n%s",
            "--numstat",
            "--no-merges",
        ],
    )
    return parse_log_output(output)


def get_repo_name(repo_root: Path) -> str:
    try:
        remote = run_git(repo_root, ["remote", "get-url", "origin"]).strip()
    except RuntimeError:
        return repo_root.name

    remote = remote.rstrip("/")
    if remote.endswith(".git"):
        remote = remote[:-4]
    return remote.split("/")[-1] or repo_root.name


def get_top_files(commits: List[dict], max_items: int) -> List[Tuple[str, dict]]:
    summary: Dict[str, dict] = {}
    for commit in commits:
        for item in commit["files"]:
            current = summary.setdefault(
                item["path"],
                {"insertions": 0, "deletions": 0, "touches": 0, "binary": False},
            )
            current["insertions"] += item["insertions"]
            current["deletions"] += item["deletions"]
            current["touches"] += 1
            current["binary"] = current["binary"] or item["binary"]

    ranked = sorted(
        summary.items(),
        key=lambda pair: (pair[1]["touches"], pair[1]["insertions"] + pair[1]["deletions"], pair[0]),
        reverse=True,
    )
    return ranked[:max_items]


def build_report(
    *,
    repo_root: Path,
    report_name: str,
    window_start: dt.datetime,
    window_end: dt.datetime,
    commits: List[dict],
    max_items: int,
) -> str:
    total_files = sum(len(commit["files"]) for commit in commits)
    total_insertions = sum(commit["insertions"] for commit in commits)
    total_deletions = sum(commit["deletions"] for commit in commits)
    repo_name = get_repo_name(repo_root)
    host = socket.gethostname()

    lines = [
        report_name,
        "",
        f"Repository: {repo_name}",
        f"Folder: {repo_root}",
        f"Machine: {host}",
        f"Window start: {window_start.isoformat()}",
        f"Window end:   {window_end.isoformat()}",
        f"Commit count: {len(commits)}",
        f"Files changed: {total_files}",
        f"Insertions: {total_insertions}",
        f"Deletions: {total_deletions}",
        "",
    ]

    if not commits:
        lines.append("No Git commits were detected in this window.")
        return "\n".join(lines) + "\n"

    lines.append("Commits")
    for index, commit in enumerate(commits[:max_items], start=1):
        lines.append(
            f"{index}. {commit['short_hash']} | {commit['author']} | {commit['date']} | {commit['subject']}"
        )
        lines.append(
            f"   files={len(commit['files'])}, +{commit['insertions']}, -{commit['deletions']}"
        )

    hidden_commits = max(0, len(commits) - max_items)
    if hidden_commits:
        lines.append(f"... and {hidden_commits} more commits")

    lines.append("")
    lines.append("Top changed files")
    for path, item in get_top_files(commits, max_items):
        binary_tag = " | binary" if item["binary"] else ""
        lines.append(
            f"- {path} | touched {item['touches']} time(s) | +{item['insertions']} -{item['deletions']}{binary_tag}"
        )

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Git-based change report for the repo and send it by email."
    )
    parser.add_argument("--root", default=".", help="Repository folder to scan.")
    parser.add_argument("--recipient", default="", help="Email recipient override.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH), help="Path to the report env file.")
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory used to store generated reports.")
    parser.add_argument("--report-name", default="Daily Git Change Report", help="Report title.")
    parser.add_argument("--max-items", type=int, default=50, help="Max entries shown in each report section.")
    parser.add_argument("--scheduled-hour", type=int, default=10, help="Hour used for the daily report window.")
    parser.add_argument("--day-offset", type=int, default=0, help="0=latest completed window, 1=previous window.")
    parser.add_argument("--since", default="", help="Explicit ISO datetime start.")
    parser.add_argument("--until", default="", help="Explicit ISO datetime end.")
    parser.add_argument("--print-only", action="store_true", help="Generate the report without sending email.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.root).resolve()
    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (repo_root / env_path).resolve()
    load_env_file(env_path)

    state_dir = Path(args.state_dir)
    if not state_dir.is_absolute():
        state_dir = (repo_root / state_dir).resolve()
    reports_dir = state_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

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

    try:
        ensure_git_repo(repo_root)
    except RuntimeError as exc:
        print(f"Current folder is not a Git repository: {exc}", file=sys.stderr)
        return 4

    now = dt.datetime.now().astimezone()
    try:
        window_start, window_end = resolve_window(
            now=now,
            scheduled_hour=args.scheduled_hour,
            since=args.since,
            until=args.until,
            day_offset=args.day_offset,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 5

    commits = get_commits(repo_root, window_start.isoformat(), window_end.isoformat())
    report_body = build_report(
        repo_root=repo_root,
        report_name=args.report_name,
        window_start=window_start,
        window_end=window_end,
        commits=commits,
        max_items=max(1, args.max_items),
    )

    report_file = reports_dir / f"{now.strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.write_text(report_body, encoding="utf-8")

    if args.print_only:
        print(report_body)
        print(f"Saved local copy at {report_file}.")
        return 0

    if not smtp_config["to_addr"]:
        print("Recipient email is missing. Set REPORT_SMTP_TO or use --recipient.", file=sys.stderr)
        return 2
    if not smtp_config["username"] or not smtp_config["password"] or not smtp_config["from_addr"]:
        print(
            "SMTP settings are incomplete. Please set REPORT_SMTP_USER, REPORT_SMTP_PASSWORD, and REPORT_SMTP_FROM.",
            file=sys.stderr,
        )
        return 3

    subject_prefix = get_env("REPORT_SUBJECT_PREFIX", "[Git Change Report]")
    subject = f"{subject_prefix} {window_start.isoformat()} -> {window_end.isoformat()}"

    try:
        send_email(subject, report_body, smtp_config)
    except Exception as exc:  # pragma: no cover
        print(f"Failed to send email: {exc}", file=sys.stderr)
        return 6

    print(f"Report sent successfully to {smtp_config['to_addr']}.")
    print(f"Saved local copy at {report_file}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
