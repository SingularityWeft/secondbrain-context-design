#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 scripts/check_spec_00.py repo
python3 -m unittest discover -s tests -p 'test_spec_00.py'
git diff --check

echo "SPEC-00 VERIFY PASS"
