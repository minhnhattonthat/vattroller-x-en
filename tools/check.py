"""check.py: the repo's one-command check (tests + width lint + all-text batch check). The pre-commit hook runs this.

Exit code is pytest's, else the width lint's (tools/lint.py, budgets.json): non-zero blocks the commit. Slow emulator tests carry the `slow` marker and are skipped here."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-m", "not slow", str(ROOT / "tests")],
                       cwd=ROOT)
    lint = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "lint.py"), "--quiet"], cwd=ROOT)
    # all shipped English: control codes match the JP, glossary terms, honorifics (D1)
    text = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "batches.py"), "check"], cwd=ROOT)
    sys.exit(r.returncode or lint.returncode or text.returncode)
