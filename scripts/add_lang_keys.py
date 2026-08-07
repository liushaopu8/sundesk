#!/usr/bin/env python3
"""Add SunDesk phase-2 localization keys to src/lang/*.rs.

Inserts the 5 new keys before the closing `].iter().cloned().collect();`
line in every lang file. en.rs is skipped (key == English text). cn.rs gets
Chinese translations; everything else gets empty values.
Idempotent: skips files that already contain "The connection is ready!".
"""

import os
import pathlib

LANG_DIR = pathlib.Path(__file__).resolve().parent.parent / "src" / "lang"

EMPTY_BLOCK = '''        ("The connection is ready!", ""),
        ("Unattended", ""),
        ("SN", ""),
        ("Enter secret code", ""),
        ("Secret code", ""),
'''

CN_BLOCK = '''        ("The connection is ready!", "连接已就绪！"),
        ("Unattended", "无人值守"),
        ("SN", "SN"),
        ("Enter secret code", "请输入暗码"),
        ("Secret code", "暗码"),
'''

CLOSING = "    ].iter().cloned().collect();"


def main() -> None:
    changed = []
    for path in sorted(LANG_DIR.glob("*.rs")):
        name = path.name
        if name == "en.rs":
            continue
        text = path.read_text(encoding="utf-8")
        if "The connection is ready!" in text:
            continue
        if CLOSING not in text:
            raise SystemExit(f"Unexpected closing pattern in {name}")
        block = CN_BLOCK if name == "cn.rs" else EMPTY_BLOCK
        new_text = text.replace(CLOSING, block + CLOSING, 1)
        path.write_text(new_text, encoding="utf-8")
        changed.append(name)
    print(f"updated {len(changed)} files: {', '.join(changed)}")


if __name__ == "__main__":
    main()
