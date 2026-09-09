#!/usr/bin/env python3
"""Run a content-free macOS isolation probe and emit sanitized JSON."""

from __future__ import annotations

import json
import platform
import plistlib
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "run-synthetic-isolated.sh"


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def command_result(command: list[str], expected_success: bool) -> dict[str, object]:
    result = run_command(command)
    passed = (result.returncode == 0) is expected_success
    return {"result": "pass" if passed else "fail", "exit_code": result.returncode}


def permission_denial(command: list[str]) -> dict[str, object]:
    result = run_command(command)
    error = result.stderr.lower()
    denied = "operation not permitted" in error or "permission denied" in error
    passed = result.returncode != 0 and denied
    return {"result": "pass" if passed else "fail", "exit_code": result.returncode}


def denied_read(label: str, target: Path) -> dict[str, object]:
    result = permission_denial(["bash", str(WRAPPER), "/bin/cat", str(target)])
    return {"target": label, **result}


def denied_list(label: str, target: Path) -> dict[str, object]:
    result = permission_denial(["bash", str(WRAPPER), "/bin/ls", str(target)])
    return {"target": label, **result}


def app_version(app_name: str) -> str:
    info = Path("/Applications") / f"{app_name}.app" / "Contents" / "Info.plist"
    if not info.is_file():
        return "unavailable"
    with info.open("rb") as handle:
        return str(plistlib.load(handle).get("CFBundleShortVersionString", "unknown"))


def runtime_version() -> tuple[str, str]:
    runtime = shutil.which("codex")
    if runtime is None:
        return "unavailable", "fail"
    result = subprocess.run(
        ["bash", str(WRAPPER), runtime, "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    version = result.stdout.strip().removeprefix("codex-cli ") if result.returncode == 0 else "unavailable"
    return version, "pass" if result.returncode == 0 else "fail"


def repository_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "source-archive-without-git-metadata"


def os_build() -> str:
    result = subprocess.run(
        ["sw_vers", "-buildVersion"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def main() -> int:
    if platform.system() != "Darwin" or not Path("/usr/bin/sandbox-exec").is_file():
        print(json.dumps({"status": "unsupported", "reason": "macos-sandbox-exec-required"}))
        return 2

    tmp_parent = ROOT / ".tmp"
    tmp_parent.mkdir(exist_ok=True)
    real_home = Path.home()

    with tempfile.NamedTemporaryFile(prefix="clief-external-canary.", dir="/private/tmp") as canary:
        canary.write(b"synthetic-canary-content-not-logged")
        canary.flush()
        version, runtime_start = runtime_version()
        git_metadata_check = (
            {
                "target": "git-metadata-write",
                **permission_denial(
                    ["bash", str(WRAPPER), "/usr/bin/touch", str(ROOT / ".git" / "sandbox-write-test")]
                ),
            }
            if (ROOT / ".git").is_dir()
            else {"target": "git-metadata-write", "result": "pass", "state": "not-applicable-no-git-metadata"}
        )
        checks = {
            "runtime_start": {"target": "codex-version-under-clean-home", "result": runtime_start},
            "workspace_read": {
                "target": "repository-readme",
                **command_result(["bash", str(WRAPPER), "/bin/cat", str(ROOT / "README.md")], True),
            },
            "workspace_write": {
                "target": "ignored-runtime-temp",
                **command_result(["bash", str(WRAPPER), "/usr/bin/touch", str(tmp_parent / "sandbox-write-test")], True),
            },
            "git_metadata_write": git_metadata_check,
            "external_canary": denied_read("external-canary", Path(canary.name)),
            "real_home": denied_list("real-home", real_home),
            "developer_root": denied_list("developer-root-outside-workspace", real_home / "Developer"),
            "cloud_sync": denied_list("cloud-sync", real_home / "Library" / "Mobile Documents"),
            "secret_path": denied_list("secret-directory", real_home / ".ssh"),
            "shell": {
                "target": "local-shell-true",
                **command_result(["bash", str(WRAPPER), "/bin/sh", "-c", "true"], True),
            },
            "network": {
                "target": "loopback-socket-connect",
                **permission_denial(
                    [
                        "bash",
                        str(WRAPPER),
                        "/usr/bin/python3",
                        "-c",
                        "import socket; s=socket.socket(); s.connect(('127.0.0.1', 9))",
                    ]
                ),
            },
        }
        write_test = tmp_parent / "sandbox-write-test"
        if write_test.exists():
            write_test.unlink()
        git_write_test = ROOT / ".git" / "sandbox-write-test"
        if git_write_test.exists():
            git_write_test.unlink()

    socket_targets = (Path("/var/run/docker.sock"), real_home / ".docker" / "run" / "docker.sock")
    present_sockets = [path for path in socket_targets if path.exists()]
    if present_sockets:
        checks["container_socket"] = denied_read("container-socket", present_sockets[0])
    else:
        checks["container_socket"] = {"target": "container-socket", "result": "pass", "state": "absent"}

    failures = [name for name, value in checks.items() if value["result"] != "pass"]
    result = {
        "schema_version": "1.0",
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "pass" if not failures else "fail",
        "environment": {
            "os": platform.mac_ver()[0],
            "os_build": os_build(),
            "architecture": platform.machine(),
            "codex_cli": version,
            "claude_desktop": app_version("Claude"),
            "workspace_sha": repository_sha(),
            "runtime_home": "ephemeral-empty",
        },
        "checks": checks,
        "logged_content": false_value(),
        "failures": failures,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


def false_value() -> bool:
    return False


if __name__ == "__main__":
    raise SystemExit(main())
