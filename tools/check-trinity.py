#!/usr/bin/env python3
"""
tools/check-trinity.py
Deterministic integrity checker for Wireframe <-> Prompt <-> Docs trinity.
Exit 0: Integrity intact.
Exit 1: Drift, broken links, or token budget breaches.
"""

import sys
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIREFRAME_DIR = ROOT / "cans/artifacts/wireframe"
PROMPT_DIR = ROOT / "cans/artifacts/prompt"
DOCS_DIR = ROOT / "docs"

ERRORS = []

def err(msg: str):
    ERRORS.append(msg)
    print(f"  [FAIL] {msg}", file=sys.stderr)

def approx_tokens(text: str) -> int:
    return max(1, int(len(text.strip()) / 3.5))

def check_triggers_and_fixtures():
    triggers_file = PROMPT_DIR / "_triggers.json"
    if not triggers_file.exists():
        err(f"Missing {triggers_file}")
        return

    try:
        triggers = json.loads(triggers_file.read_text())
    except Exception as e:
        err(f"Malformed JSON in {triggers_file}: {e}")
        return

    for t in triggers.get("triggers", []):
        sid = t.get("screen_id")
        parts = sid.split(".")
        if len(parts) != 4:
            err(f"Trigger {t.get('id')}: screen_id '{sid}' violates 4-segment naming law")
            continue
        noun, verb = parts[0], parts[1]
        fixture_path = WIREFRAME_DIR / "screens" / noun / verb / f"{sid}.json"
        if not fixture_path.exists():
            err(f"Trigger {t.get('id')} references missing fixture: {fixture_path.relative_to(ROOT)}")

    for fix_file in (WIREFRAME_DIR / "screens").glob("**/*.json"):
        try:
            data = json.loads(fix_file.read_text())
        except Exception:
            continue
        
        trailer = data.get("trailer")
        if trailer:
            ptr = trailer.get("prompt", "")
            if not ptr.startswith("prompt://"):
                err(f"{fix_file.name}: invalid trailer prompt scheme: '{ptr}'")
            
            reason = trailer.get("reason", "")
            trailer_str = f"trailer: {ptr} - {reason}"
            tokens = approx_tokens(trailer_str)
            if tokens > 30:
                err(f"{fix_file.name}: L1 trailer exceeds 30 tokens ({tokens} tokens): '{trailer_str}'")

def check_prompt_to_docs():
    doc_ref_pattern = re.compile(r"doc://([a-zA-Z0-9_\-\/]+)(?:#([a-zA-Z0-9_\-]+))?")
    
    for prompt_file in PROMPT_DIR.glob("**/*.md"):
        content = prompt_file.read_text()
        tokens = approx_tokens(content)
        if tokens > 500:
            err(f"Prompt leaf {prompt_file.relative_to(ROOT)} exceeds 500 tokens ({tokens} tokens)")
            
        for match in doc_ref_pattern.finditer(content):
            doc_path, anchor = match.group(1), match.group(2)
            target_md = DOCS_DIR / f"{doc_path}.md"
            
            if not target_md.exists():
                err(f"Broken doc link in {prompt_file.name}: 'doc://{doc_path}' -> {target_md.relative_to(ROOT)} not found")
                continue
                
            if anchor:
                doc_text = target_md.read_text()
                header_pattern = re.compile(rf"^#+\s+.*", re.MULTILINE)
                slugs = [
                    re.sub(r"[^\w\- ]", "", h.lstrip("#").strip()).lower().replace(" ", "-")
                    for h in header_pattern.findall(doc_text)
                ]
                if anchor.lower() not in slugs:
                    err(f"Broken anchor in {prompt_file.name}: 'doc://{doc_path}#{anchor}' not in {target_md.name}")

def main():
    print("Verifying Trinity Integrity (wireframe <-> prompt <-> docs)...")
    check_triggers_and_fixtures()
    check_prompt_to_docs()
    
    if ERRORS:
        print(f"\n[FAIL] Found {len(ERRORS)} Trinity integrity violation(s).", file=sys.stderr)
        sys.exit(1)
    
    print("[PASS] Trinity locked. Zero broken links. All token cages enforced.")
    sys.exit(0)

if __name__ == "__main__":
    main()
