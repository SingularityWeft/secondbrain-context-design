#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$(uname -s)" != "Darwin" ]] || [[ ! -x /usr/bin/sandbox-exec ]]; then
  echo "RUNTIME_UNSUPPORTED: macOS sandbox-exec fehlt" >&2
  exit 2
fi
if [[ $# -eq 0 ]]; then
  echo "Aufruf: bash scripts/run-synthetic-isolated.sh BEFEHL" >&2
  exit 2
fi
if [[ "$repo_root" == *'"'* ]] || [[ "$repo_root" == *$'\n'* ]]; then
  echo "RUNTIME_UNSUPPORTED: Repository-Pfad ist nicht sicher darstellbar" >&2
  exit 2
fi

mkdir -p "$repo_root/.tmp"
runtime_dir="$(mktemp -d "$repo_root/.tmp/runtime.XXXXXX")"
cleanup() {
  chmod -R u+w "$runtime_dir" 2>/dev/null || true
  rm -rf -- "$runtime_dir"
}
trap cleanup EXIT
mkdir -p "$runtime_dir/home" "$runtime_dir/codex" "$runtime_dir/tmp"

real_home="$(cd && pwd)"
profile="(version 1)
(allow default)
(deny file-read* file-write* (subpath \"$real_home\") (subpath \"/private/tmp\") (subpath \"/tmp\") (subpath \"/Volumes\") (subpath \"/Network\"))
(allow file-read* file-write* (subpath \"$repo_root\"))
(deny file-write* (subpath \"$repo_root/.git\"))
(deny file-read* file-write* (literal \"/var/run/docker.sock\") (literal \"$real_home/.docker/run/docker.sock\"))
(deny network*)"

env -i \
  HOME="$runtime_dir/home" \
  CODEX_HOME="$runtime_dir/codex" \
  TMPDIR="$runtime_dir/tmp" \
  PATH="/usr/bin:/bin:/usr/sbin:/sbin:/Applications/ChatGPT.app/Contents/Resources" \
  LANG="C.UTF-8" \
  /usr/bin/sandbox-exec -p "$profile" "$@"
