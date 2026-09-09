#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ -n "${CLIEF_PRIVATE_DENYLIST:-}" ]]; then
  python3 scripts/check_repository.py --private-denylist "$CLIEF_PRIVATE_DENYLIST"
  python3 scripts/check_public_history.py --private-denylist "$CLIEF_PRIVATE_DENYLIST"
else
  python3 scripts/check_repository.py
  python3 scripts/check_public_history.py
fi

python3 scripts/check_skills.py
python3 scripts/check_pilot.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/run_e2e.py >/dev/null
git diff --check
git diff --cached --check

echo "VERIFY_REPO_PASS"
