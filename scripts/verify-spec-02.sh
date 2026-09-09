#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/verify-spec-01.sh
python3 -m unittest discover -s tests -p 'test_spec_02.py'
git diff --check

echo "SPEC-02 VERIFY PASS"
