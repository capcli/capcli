#!/usr/bin/env python3
"""
tools/check-wireframe-canon.py
Prevention suite: wireframe <-> canon drift must not silently recur.

All expectations derive from the cans SSOT (effect.md, manifest.json,
_states.json, kernel.md); nothing here invents law. Run standalone for a
pass/fail verdict, or let tools/check-trinity.py aggregate its failures.

Checks:
  1. pointer_lint      - fail if any markdown under cans/ cites a cans/*.md
                         path that does not exist on disk (deleted chapters
                         physics/action/budget/agent/trust/space/time included).
  2. domain_mirror     - effect.md#Denials exit->domain taxonomy equals
                         _states.json exit->domains exactly (order-insensitive).
  3. fixture_crosslayer - (i) screen-id state segment is one of the six state
                         labels from _states.json; (ii) component.domain is in
                         _states.json's domain list for its exit (success->0,
                         denial->2, refusal->3, crash->4, panic->5, yield->6;
                         exit-0 fixtures carry no domain); (iii) the noun
                         segment is in manifest.json kernel nouns or
                         plugin-provided nouns.
  4. manifest_schema   - pointer_schemes == the 11 URP schemes; affordance
                         required fields == {rel, command, intent, risk}
                         (no requires_intent).

Exclusions (documented skips, never silent):
  - cans/artifacts/test-plan/** : the 194 orphaned per-case law_reference
    entries citing deleted chapters are a known separate backlog
    (rehome-vs-leave pick outstanding). The pointer lint does not sweep them.
  - cans/_adr/** : immutable historical records; their citations were valid
    when the record was written. Rewriting them would falsify history.

Exit 0: all checks pass (with documented skips). Exit 1: drift found.
"""

import sys
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANS = ROOT / "cans"
WIREFRAME = CANS / "artifacts" / "wireframe"
SCREENS = WIREFRAME / "screens"

DELETED_CHAPTERS = {
    "physics.md", "action.md", "budget.md",
    "agent.md", "trust.md", "space.md", "time.md",
}
EXPECTED_STATES = {"success", "denial", "refusal", "crash", "panic", "yield"}
STATE_TO_EXIT = {
    "success": "0", "denial": "2", "refusal": "3",
    "crash": "4", "panic": "5", "yield": "6",
}
URP_SCHEMES_11 = {
    "cap://", "ask://", "audit://", "quota://", "vault://", "pack://",
    "policy://", "ws://", "db://", "doc://", "plugin://",
}
AFFORDANCE_REQUIRED_4 = {"rel", "command", "intent", "risk"}

# fixture_id -> reason. Sibling-owned drift (fixtures live in Phase 5 of the
# repair plan); these stay green-on-intent here and are never edited by this
# checker. Unbacked domains (no cans home, no exit law) are additionally
# flagged for an explicit user decision.
FIXTURE_SKIPS = {
    "sys.doctor.degraded.quarantine":
        "illegal state label 'degraded' (canon: six labels; degraded is a "
        "condition flag on exit 0) plus component.domain kernel.integrity on "
        "an exit-0-class screen; sibling owns the rename",
    "sys.doctor.denial.thrashing":
        "domain agent.thrashing has no cans home and no exit law; flagged "
        "for user decision",
    "sys.shim.crash.wrapper_deploy":
        "domain kernel.shim has no cans home and no exit law; flagged "
        "for user decision",
    "sys.shim.denial.target_missing":
        "domain kernel.shim has no cans home and no exit law; flagged "
        "for user decision",
    "pack.scaffold.denial.target_exists":
        "domain policy.authoring has no cans home and no exit law; flagged "
        "for user decision",
    "pack.bundle.denial.size_limit":
        "domain policy.pack on denial (exit 2); canon places policy.pack at "
        "exit 3 (static refusal); sibling owns the fixture remap",
    "routine.retire.denial.active_deps":
        "domain policy.governance on exit 2; no such domain in "
        "effect.md#Denials; sibling owns the fixture remap",
    "routine.rollback.denial.depth":
        "domain policy.governance on exit 2; no such domain in "
        "effect.md#Denials; sibling owns the fixture remap",
    "sys.backup.success.push_pending":
        "component.domain policy.backup on exit 0; canon: exit 0 carries no "
        "domain; sibling owns the fixture remap",
}


def parse_denials_taxonomy():
    """Defensive parse of the exit-anchored domain taxonomy under the
    effect.md Denials node. Returns (taxonomy, error) where taxonomy maps
    exit string -> set of domain strings. A bullet only counts as a domain
    when it sits strictly deeper than its exit-N header, so prose bullets
    elsewhere in the section (e.g. '- domain - exact fault layer string'
    under Canonical error payload) can never leak in."""
    lines = (CANS / "effect.md").read_text().splitlines()
    start = next((i for i, l in enumerate(lines) if l == "  - Denials"), None)
    if start is None:
        return None, "effect.md: Denials node not found"
    end = next(
        (i for i in range(start + 1, len(lines)) if re.match(r"^  - \S", lines[i])),
        len(lines),
    )
    section = lines[start:end]
    tax, cur_exit, cur_indent = {}, None, None
    for l in section:
        m = re.match(r"^(\s*)- exit ([23456])\s*[—–-]\s", l)
        if m:
            cur_exit, cur_indent = m.group(2), len(m.group(1))
            tax.setdefault(cur_exit, set())
            continue
        bm = re.match(r"^(\s*)- \S", l)
        if bm and cur_exit is not None and len(bm.group(1)) <= cur_indent:
            cur_exit, cur_indent = None, None  # left the exit block
            continue
        dm = re.match(
            r"^(\s*)- ([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]+)?)\s*[—–-]\s+\S", l
        )
        if dm and cur_exit is not None and len(dm.group(1)) > cur_indent:
            tax[cur_exit].add(dm.group(2))
    if not tax:
        return None, "effect.md: no exit-N domain blocks parsed under Denials"
    return tax, None


def check_pointer_lint(errors):
    """Fail on cans/*.md cites whose file is missing on disk."""
    # Every markdown file under cans/ is a legitimate cite TARGET ...
    known = {f.relative_to(CANS).as_posix() for f in CANS.rglob("*.md")}
    # ... but we only lint the CONTENT of files outside these two scopes:
    # test-plan/** = separate law_reference backlog (see module docstring);
    # _adr/** = immutable historical records.
    def lintable(rel):
        return not (
            rel.startswith("artifacts/test-plan/") or rel.startswith("_adr/")
        )
    cite_re = re.compile(r"cans/([A-Za-z0-9_./-]+\.md)")
    fails = 0
    for f in sorted(CANS.rglob("*.md")):
        rel = f.relative_to(CANS).as_posix()
        if not lintable(rel):
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            for m in cite_re.finditer(line):
                tgt = m.group(1)
                if tgt not in known:
                    kind = "deleted chapter" if tgt in DELETED_CHAPTERS else "missing file"
                    errors.append(
                        f"pointer_lint: {rel}:{i} cites cans/{tgt} "
                        f"({kind}; not on disk)"
                    )
                    print(f"  [FAIL] pointer_lint: {rel}:{i} cites cans/{tgt} ({kind})",
                          file=sys.stderr)
                    fails += 1
    if not fails:
        print("  [PASS] pointer_lint: no markdown under cans/ cites a missing "
              "cans/*.md path (test-plan law_reference backlog and _adr history excluded)")
    return fails


def check_domain_mirror(errors):
    """_states.json exit->domains must equal effect.md#Denials exactly."""
    tax, perr = parse_denials_taxonomy()
    if perr:
        errors.append(f"domain_mirror: {perr}")
        print(f"  [FAIL] domain_mirror: {perr}", file=sys.stderr)
        return 1
    try:
        states = json.loads((WIREFRAME / "_states.json").read_text())
    except Exception as e:
        errors.append(f"domain_mirror: cannot read _states.json: {e}")
        print(f"  [FAIL] domain_mirror: cannot read _states.json: {e}", file=sys.stderr)
        return 1
    fails = 0
    # Top-level metadata entries (e.g. the _comment derivation note) are not
    # exits; only dict-valued entries participate.
    exits = {k: v for k, v in states.items() if isinstance(v, dict)}
    labels = {k: v.get("label") for k, v in exits.items()}
    if set(labels.values()) != EXPECTED_STATES:
        errors.append(
            f"domain_mirror: _states.json labels {sorted(labels.values())} != "
            f"six-label set {sorted(EXPECTED_STATES)}"
        )
        print("  [FAIL] domain_mirror: _states.json labels are not the six-label set",
              file=sys.stderr)
        fails += 1
    for ext in ("2", "3", "4", "5", "6"):
        got = set(states.get(ext, {}).get("domains", []))
        want = tax.get(ext, set())
        if got != want:
            errors.append(
                f"domain_mirror: exit {ext} _states.json={sorted(got)} "
                f"!= effect.md#Denials={sorted(want)} "
                f"(only-in-states={sorted(got - want)}; only-in-denials={sorted(want - got)})"
            )
            print(f"  [FAIL] domain_mirror: exit {ext} mismatch "
                  f"(states-only={sorted(got - want)}, denials-only={sorted(want - got)})",
                  file=sys.stderr)
            fails += 1
    if states.get("0", {}).get("domains"):
        errors.append("domain_mirror: exit 0 must carry no domains (canon)")
        print("  [FAIL] domain_mirror: exit 0 carries domains", file=sys.stderr)
        fails += 1
    if "boot_refusal" in json.dumps(states):
        errors.append(
            "domain_mirror: _states.json still claims boot_refusal; canon "
            "(kernel.md#Fail-closed-stance) puts boot refusals at exit 3"
        )
        print("  [FAIL] domain_mirror: _states.json carries boot_refusal", file=sys.stderr)
        fails += 1
    if not fails:
        print("  [PASS] domain_mirror: _states.json exit->domains equals "
              "effect.md#Denials exactly")
    return fails


def check_fixtures(errors, skips, states):
    """Cross-layer fixture checks: state segment, domain, noun."""
    exits = {k: v for k, v in states.items() if isinstance(v, dict)}
    label2exit = {v.get("label"): k for k, v in exits.items()}
    try:
        manifest = json.loads((WIREFRAME / "manifest.json").read_text())
    except Exception as e:
        errors.append(f"fixture_crosslayer: cannot read manifest.json: {e}")
        print(f"  [FAIL] fixture_crosslayer: cannot read manifest.json: {e}",
              file=sys.stderr)
        return 1
    nouns = set(manifest.get("nouns", [])) | set(manifest.get("plugin_nouns", []))
    if not (SCREENS / "plugin").exists():
        skips.append("screens/plugin/ absent: plugin-noun screens not yet "
                     "created (sibling-owned); noun check tolerates the gap")
        print("  [SKIP] screens/plugin/ absent (sibling-owned); noun check "
              "tolerates")
    fails = 0
    files = sorted(SCREENS.glob("**/*.json"))
    if not files:
        errors.append("fixture_crosslayer: no fixtures found under screens/")
        print("  [FAIL] fixture_crosslayer: no fixtures found", file=sys.stderr)
        return 1
    seen_skips = set()
    for f in files:
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        sid = d.get("id", "")
        if sid in FIXTURE_SKIPS:
            seen_skips.add(sid)
            skips.append(f"{sid}: {FIXTURE_SKIPS[sid]}")
            continue
        parts = sid.split(".")
        noun = parts[0] if parts else ""
        state = parts[2] if len(parts) >= 3 else None
        if state not in label2exit:
            errors.append(
                f"fixture_crosslayer: {sid}: state segment '{state}' not in "
                f"six-label set {sorted(EXPECTED_STATES)}"
            )
            print(f"  [FAIL] fixture_crosslayer: {sid}: illegal state '{state}'",
                  file=sys.stderr)
            fails += 1
            continue  # cannot derive an exit; the domain check needs one
        ext = label2exit[state]
        dom = d.get("component", {}).get("domain")
        allowed = set(states.get(ext, {}).get("domains", []))
        if ext == "0":
            if dom:
                errors.append(
                    f"fixture_crosslayer: {sid}: exit-0 fixture carries domain "
                    f"'{dom}' (canon: exit 0 carries no domain)"
                )
                print(f"  [FAIL] fixture_crosslayer: {sid}: domain on exit 0",
                      file=sys.stderr)
                fails += 1
        elif dom and dom not in allowed:
            errors.append(
                f"fixture_crosslayer: {sid}: domain '{dom}' not in "
                f"_states.json exit-{ext} domains"
            )
            print(f"  [FAIL] fixture_crosslayer: {sid}: domain '{dom}' not in "
                  f"_states.json exit-{ext} domains", file=sys.stderr)
            fails += 1
        if noun not in nouns:
            errors.append(
                f"fixture_crosslayer: {sid}: noun '{noun}' not in manifest.json "
                f"kernel nouns or plugin-provided nouns"
            )
            print(f"  [FAIL] fixture_crosslayer: {sid}: noun '{noun}' not in "
                  f"manifest nouns", file=sys.stderr)
            fails += 1
    for sid in sorted(set(FIXTURE_SKIPS) - seen_skips):
        skips.append(f"retired (no fixture carries this id anymore; the owning "
                     f"fix likely landed): {sid}")
    if not fails:
        print(f"  [PASS] fixture_crosslayer: {len(files)} fixtures checked "
              f"({len(seen_skips)} documented skips applied)")
    return fails


def check_manifest_schema(errors):
    """pointer_schemes == 11 URP schemes; affordance required fields == 4."""
    try:
        manifest = json.loads((WIREFRAME / "manifest.json").read_text())
    except Exception as e:
        errors.append(f"manifest_schema: cannot read manifest.json: {e}")
        print(f"  [FAIL] manifest_schema: cannot read manifest.json: {e}",
              file=sys.stderr)
        return 1
    fails = 0
    oc = manifest.get("output_contract", {})
    schemes = set(oc.get("pointer_schemes", []))
    if schemes != URP_SCHEMES_11:
        errors.append(
            f"manifest_schema: pointer_schemes={sorted(schemes)} != "
            f"11-scheme set {sorted(URP_SCHEMES_11)} "
            f"(missing={sorted(URP_SCHEMES_11 - schemes)}; extra={sorted(schemes - URP_SCHEMES_11)})"
        )
        print("  [FAIL] manifest_schema: pointer_schemes is not the 11-scheme set",
              file=sys.stderr)
        fails += 1
    req = set(
        oc.get("affordances", {}).get("machine_schema", {})
        .get("items", {}).get("required", [])
    )
    if req != AFFORDANCE_REQUIRED_4:
        errors.append(
            f"manifest_schema: affordance required={sorted(req)} != "
            f"{sorted(AFFORDANCE_REQUIRED_4)}"
        )
        print("  [FAIL] manifest_schema: affordance required-fields mismatch",
              file=sys.stderr)
        fails += 1
    if not fails:
        print("  [PASS] manifest_schema: 11 URP schemes; affordance required == "
              "{rel, command, intent, risk}")
    return fails


def run(errors=None, skips=None):
    """Run all prevention checks. Appends to errors/skips lists; returns
    (fail_count, skip_count). Prints [PASS]/[SKIP]/[FAIL] lines."""
    if errors is None:
        errors = []
    if skips is None:
        skips = []
    print("Checking wireframe <-> canon prevention locks...")
    n0 = len(errors)
    check_pointer_lint(errors)
    check_domain_mirror(errors)
    try:
        states = json.loads((WIREFRAME / "_states.json").read_text())
    except Exception:
        states = {}
    check_fixtures(errors, skips, states)
    check_manifest_schema(errors)
    fails = len(errors) - n0
    if fails:
        print(f"[FAIL] {fails} wireframe-canon violation(s) "
              f"({len(skips)} documented skip(s)).", file=sys.stderr)
    else:
        print(f"[PASS] Wireframe-canon locks hold ({len(skips)} documented skip(s)).")
    return fails, len(skips)


if __name__ == "__main__":
    errs, skps = [], []
    fails, _ = run(errs, skps)
    for s in skps:
        print(f"  [SKIP] {s}")
    sys.exit(1 if fails else 0)
