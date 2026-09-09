#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/verify-spec-02.sh
python3 scripts/check_skills.py
python3 -m unittest discover -s tests -p 'test_spec_03.py'
git diff --check

echo "SPEC-03 VERIFY PASS"
