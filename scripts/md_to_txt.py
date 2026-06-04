#!/usr/bin/env python3
"""Render the tailored resume markdown into clean plain text for Google Docs.

Strips markdown markup (#, **, *, links) and normalises bullets/spacing so the
text uploads to Drive as a readable, editable Google Doc.
"""
import re
from pathlib import Path

LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def clean(md_text: str) -> str:
    out = []
    for raw in md_text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            out.append("")
            continue
        line = LINK_RE.sub(r"\1", line)
        line = line.replace("**", "").replace("*", "")
        if line.startswith("# "):
            out.append(line[2:].strip().upper())
        elif line.startswith("## "):
            out.append("")
            out.append(line[3:].strip().upper())
        elif line.startswith("- "):
            out.append("• " + line[2:].strip())
        else:
            out.append(line.strip())
    # collapse 3+ blank lines to 1
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def main():
    src = Path("resumes/tailored")
    out = src / "txt"
    out.mkdir(exist_ok=True)
    for md in sorted(src.glob("*.md")):
        if md.name == "README.md":
            continue
        (out / (md.stem + ".txt")).write_text(clean(md.read_text(encoding="utf-8")),
                                               encoding="utf-8")
        print("wrote", out / (md.stem + ".txt"))


if __name__ == "__main__":
    main()
