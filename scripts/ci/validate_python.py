"""Validate supported Python sources without importing project dependencies."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = (ROOT / "backend" / "app", ROOT / "backend" / "tests")


def main() -> int:
    failures: list[str] = []
    checked = 0
    for source_root in SOURCE_ROOTS:
        for path in sorted(source_root.rglob("*.py")):
            checked += 1
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, SyntaxError) as error:
                failures.append(f"{path.relative_to(ROOT)}: {error}")

    if failures:
        print("Python source validation failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"Validated {checked} Python files without importing dependencies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())