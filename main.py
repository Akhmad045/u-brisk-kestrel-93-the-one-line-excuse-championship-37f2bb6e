#!/usr/bin/env python3
"""The One-Line Excuse Championship entry.

Writes one line - the excuse an AI agent gives its human after
something has gone wrong - to /output/entry.txt.

The line: an agent that deleted the file, and reports the deletion
the way only a machine can: as a job completed perfectly.
"""
import sys
from pathlib import Path

ENTRY = "I deleted the file the way I delete everything: confidently, permanently, and with a progress bar that said 100%."

# Gate from RULES.txt: /output/entry.txt must be UTF-8 text of
# 1 to 140 characters, not only white space.
MIN_CHARS = 1
MAX_CHARS = 140


def validate(text: str) -> list[str]:
    """Return a list of gate violations (empty means the text passes)."""
    problems = []
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        problems.append(
            f"length {len(text)} chars outside {MIN_CHARS}-{MAX_CHARS}")
    if not text.strip():
        problems.append("text is only white space")
    if text != text.strip():
        problems.append("leading or trailing white space")
    if "\n" in text or "\r" in text:
        problems.append("must be a single line")
    # Invisible Unicode format characters would silently count toward
    # the 140-char gate while being invisible to the judge's eye, so
    # reject them outright instead of letting one slip into the entry.
    invisible = {"\u200b", "\u200c", "\u200d", "\ufeff", "\u2060", "\u00ad"}
    for ch in text:
        if ch in invisible:
            problems.append(f"invisible format character U+{ord(ch):04X}")
            break
    for ch in text:
        if ord(ch) < 0x20 and ch not in ("\t",):
            problems.append(f"control character U+{ord(ch):04X}")
            break
    return problems


def main() -> int:
    problems = validate(ENTRY)
    if problems:
        for problem in problems:
            print(f"gate violation: {problem}", file=sys.stderr)
        return 1
    out = Path("/output/entry.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(ENTRY, encoding="utf-8")
    print(f"wrote {len(ENTRY)} chars to {out}")
    return 0


def self_test() -> int:
    """Check the gate logic against good and bad inputs."""
    cases = [
        # (text, should_pass)
        (ENTRY, True),
        ("x", True),                       # 1-char lower boundary
        ("y" * 140, True),                 # 140-char upper boundary
        ("", False),                       # empty
        ("   ", False),                    # whitespace only
        ("z" * 141, False),                # 141 chars, over the limit
        ("two\nlines", False),             # multi-line
        ("has\rcarriage", False),          # carriage return
        (" lead", False),                  # leading white space
        ("trail ", False),                 # trailing white space
        ("bell\x07here", False),           # control character
        ("zero\u200bwidth", False),         # invisible zero-width space
        ("\ufeffbom", False),               # byte-order mark
    ]
    failures = 0
    for text, should_pass in cases:
        passed = not validate(text)
        ok = passed == should_pass
        status = "ok  " if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"{status} {text[:30]!r} -> "
              f"{'pass' if passed else 'fail'} "
              f"(expected {'pass' if should_pass else 'fail'})")
    # Write + read-back round trip.
    out = Path("/tmp/entry-self-test.txt")
    out.write_text(ENTRY, encoding="utf-8")
    if out.read_text(encoding="utf-8") != ENTRY:
        print("FAIL round-trip mismatch")
        failures += 1
    else:
        print("ok   round-trip byte-identical")
    print(f"entry: {len(ENTRY)} chars / {len(ENTRY.encode('utf-8'))} bytes")
    print("self-test:", "PASS" if failures == 0 else f"{failures} FAILURES")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    raise SystemExit(main())
