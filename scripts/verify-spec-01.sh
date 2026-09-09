#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/verify-spec-00.sh
python3 -m unittest discover -s tests -p 'test_spec_01.py'
python3 scripts/runtime_isolation_probe.py >/dev/null
git diff --check

echo "SPEC-01 VERIFY PASS"
