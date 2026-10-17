#!/usr/bin/env python3
r"""
tools/validate_wireframe_v1.py
Validator for the wireframe/v1 screen grammar (plan-2 §R10).

Zero third-party dependencies; plain python3; exit 0 green, exit 1 breach.
Runbook §R14 step 2. Supersedes the retired string-assertion validator:
every checked position accepts a string literal OR a $slot / $interpolate
object satisfying the slot grammar declared in
manifest.json#output_contract.slot (that block is read LIVE; until it
lands, the built-in DEFAULT_SLOT_CONTRACT below — diff-patches §1 extended
with plan-2 §R3/§R9 — is used, and the fallback is reported).

Checks (task 3-b scope):
  1.  $schema is exactly "wireframe/v1" (any v2 residue is an error).
  2.  Slot grammar — $slot requires $from + $example; $interpolate requires
      $bindings + $example; $kind is "instance" or absent ($kind:"semantic"
      is a hard error anywhere); optional $type/$pattern/$enum are honored
      against $example; the $-key set is closed (unknown structural $-keys
      error); $example is a JSON scalar (string/number/boolean — 3-c
      reconciliation: boolean $examples are the current literal on
      boolean component fields, e.g. has_more); $interpolate placeholders are
      all bound; when every binding resolves statically (scenario/context/
      world) the substituted template must equal $example.
  3.  Semantic positions (manifest semantic_positions, live) never carry a
      $slot/$interpolate — id, $schema, archetype, rule, domain, layer,
      remedy, context.{env,tier,trust}, trailer.prompt, attention.*.class,
      isolated, isolated_reason. Bare entries match the root key or the
      same key at component root; '[]'/'[*]'/'*' segments are wildcards.
  4.  Volatility (plan-2 §R2): root elapsed_ms is always a $slot, never a
      literal; time-like component strings (durations "12ms"/"4h 12m",
      clock times "18:00:00 UTC", next_fire/reset_at/measured time-cites)
      are slots, never literals. The detector is documented below; its hit
      count is reported by --summary (plan-2 cites ≈97 hits).
  5.  Binding paths: every $from / $bindings value matches
      ^(context|scenario|world|live)(\.[a-z_][a-z0-9_]*|\[\d+\])+$  (§R7).
  6.  Binding closure: scenario.* paths resolve in the screen's scenario
      block, context.* in the context block, world.* requires a root world
      block; live.* is extracted at assertion time and is not statically
      checked. Reverse direction: scenario keys referenced by no slot are
      WARN-only (§R8 bounds the block to what slots reference; dead keys
      are noise, not breach). The scenario/world blocks are binding data
      (plan.md §5): $-keys are not legal there.
  7.  Affordance attestation (preserved law): affordances exist on exit-0
      screens only; rel enum and required fields from the manifest
      affordances machine_schema (fallback {next,abort,inspect} /
      {rel,command,intent,risk}); risk in {safe,mutating}; requires_intent
      is a derived field — if authored it must sit on a mutating affordance
      (the manifest machine_schema carries no requires_intent, so presence
      on mutating is accepted but never demanded; deviation from the
      literal iff-law is recorded in the worklog). The instantiated
      affordance command must equal the $example of some command-bearing
      $slot/$interpolate in the validated set where resolvable; commands
      with no modeled screen are counted as unresolvable, not errors.
  8.  Trailer law: trailer present iff the screen id is named in
      cans/artifacts/prompt/_triggers.json; root next_action never appears
      on a screen; trailer.prompt is a semantic literal; prompt/reason/
      serve validate against the manifest trailer machine_schema.
  9.  Archetype structural checks (wireframe-structure.md §6.1 Component
      law, preserved): diagnostic carries domain+culprit+remedy; rule and
      layer, where present, are literals; tree carries title+root+nodes
      with {label, children} recursion; receipt carries groups of
      {title?, fields?, lines?}; document carries header_badge+body (+ the
      items/next_cursor/has_more pagination envelope where truncation is
      present). Exit code derives from the id state segment (success 0,
      denial 2, refusal 3, crash 4, panic 5, yield 6); exits 2-6 are
      diagnostic, exit 0 is receipt/tree/document; component.domain must
      agree with _states.json (canon's documented fixture skips apply).
 10.  isolated / isolated_reason appear only on sys.shim.* fixtures and
      pass through untouched (plan-2 §R9).
 11.  No banned substring "template" in any key or value under screens/**
      (plan.md §3/§11.1 guardrail).

CLI:  python3 tools/validate_wireframe_v1.py [--verbose] [--summary] [paths...]
      No paths -> every screen under cans/artifacts/wireframe/screens/.
      Paths may be files or directories (only *.json are validated).
Exit: 0 all green; 1 errors found.
"""

import json
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIREFRAME = ROOT / "cans" / "artifacts" / "wireframe"
SCREENS = WIREFRAME / "screens"
TRIGGERS = ROOT / "cans" / "artifacts" / "prompt" / "_triggers.json"

# --------------------------------------------------------------------------
# Slot contract (manifest#output_contract.slot read live; this is fallback)
# --------------------------------------------------------------------------
DEFAULT_SLOT_CONTRACT = {
    "schema": "wireframe/v1",
    "keys": ["$slot", "$interpolate"],
    "slot_requires": ["$from", "$example"],
    "slot_optional": ["$kind", "$type", "$pattern", "$enum"],
    "interpolate_requires": ["$bindings", "$example"],
    "kind_enum": ["instance"],
    "binding_prefixes": ["context", "scenario", "world", "live"],
    "semantic_positions": [
        "id", "$schema", "archetype", "rule", "domain", "layer",
        "remedy", "context.env", "context.tier", "context.trust",
        "trailer.prompt", "attention.*.class",
        "isolated", "isolated_reason",
    ],
    "banned_substring_in_screens": ["template"],
}

SLOT_FORM_KEYS = {"$slot", "$from", "$example", "$kind", "$type", "$pattern", "$enum"}
INTERP_FORM_KEYS = {"$interpolate", "$bindings", "$example"}
BINDING_RE = re.compile(r"^(context|scenario|world|live)(\.[a-z_][a-z0-9_]*|\[\d+\])+$")
SLOT_NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
}

STATE_TO_EXIT = {"success": "0", "denial": "2", "refusal": "3",
                 "crash": "4", "panic": "5", "yield": "6"}
EXIT_ARCHETYPES = {
    "0": {"tree", "receipt", "document"},
    "2": {"diagnostic"}, "3": {"diagnostic"}, "4": {"diagnostic"},
    "5": {"diagnostic"}, "6": {"diagnostic"},
}
DEFAULT_REL_ENUM = {"next", "abort", "inspect"}
DEFAULT_RISK_ENUM = {"safe", "mutating"}
DEFAULT_AFFORDANCE_REQUIRED = {"rel", "command", "intent", "risk"}

# --------------------------------------------------------------------------
# Volatility detector (plan-2 §R2). Two signals, unioned:
#   (a) the key name cites time (reset_at / next_fire / measured / windows /
#       remaining budgets / leases / holders / timeouts / last_* ...);
#   (b) the string value carries a clock time ("18:00:00 UTC") or a
#       duration ("12ms", "4h 12m", "5-minute", "18h 24m ago", "300s").
# plan-2 §R2 cites ~97 volatile string hits; --summary reports the count
# this detector measures (definition above), never a fudged number.
# --------------------------------------------------------------------------
TIME_KEY_RE = re.compile(
    r"(?:^|_)(reset_at|next_fire|last_fire|last_run_at|measured|timeout|"
    r"window|uptime|cooldown|lease|holder|remaining|ttl|last_)(?:$|_)",
    re.I,
)
TIME_CLOCK_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:UTC|utc|Z)\b")
TIME_DURATION_RE = re.compile(
    r"\b\d+(?:\.\d+)?[\s\-]?(?:ms|us|μs|seconds?|secs?|minutes?|mins?|"
    r"hours?|hrs?|days?|weeks?|[smhd])(?![a-z0-9])",
    re.I,
)


def is_time_like(key, value):
    if not isinstance(value, str):
        return False
    if TIME_CLOCK_RE.search(value) or TIME_DURATION_RE.search(value):
        return True
    return bool(key and TIME_KEY_RE.search(str(key)))


# --------------------------------------------------------------------------
# Registry / config loaders
# --------------------------------------------------------------------------
def load_json(path):
    try:
        return json.loads(path.read_text()), None
    except Exception as e:  # malformed or missing
        return None, str(e)


def load_manifest_contract():
    """Read output_contract.slot live from manifest.json so the manifest
    stays the single home of the grammar. Returns (contract, note)."""
    manifest, err = load_json(WIREFRAME / "manifest.json")
    if manifest is None:
        return dict(DEFAULT_SLOT_CONTRACT), \
            f"manifest.json unreadable ({err}); built-in slot contract used"
    slot = manifest.get("output_contract", {}).get("slot")
    if not isinstance(slot, dict):
        return dict(DEFAULT_SLOT_CONTRACT), \
            "manifest#output_contract.slot absent (pre-3-d tree); built-in slot contract used"
    contract = dict(DEFAULT_SLOT_CONTRACT)
    contract.update({k: v for k, v in slot.items() if v is not None})
    return contract, None


def load_states():
    states, _ = load_json(WIREFRAME / "_states.json")
    return states or {}


def load_trigger_ids():
    trig, err = load_json(TRIGGERS)
    if trig is None:
        return None, err
    return {t.get("screen_id") for t in trig.get("triggers", []) if t.get("screen_id")}, None


def load_canon_fixture_skips():
    """Import check-wireframe-canon.py's documented FIXTURE_SKIPS so the
    state-taxonomy checks skip exactly what canon skips (single home for
    the skip list). Returns {} if the import fails."""
    try:
        spec = importlib.util.spec_from_file_location(
            "check_wireframe_canon_for_v1",
            Path(__file__).resolve().parent / "check-wireframe-canon.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return dict(getattr(mod, "FIXTURE_SKIPS", {}))
    except Exception:
        return {}


# --------------------------------------------------------------------------
# Semantic-position pattern matching
# --------------------------------------------------------------------------
def expand_semantic_entry(entry):
    """One semantic_positions entry -> list of segment-matcher lists.
    Bare names match the root key or the same key at component root
    (id/archetype live at root; rule/domain/layer/remedy at component
    root). 'name[]'/'name[*]' expands to name + any-index; '*' and '[]'
    match any single key or index."""
    entry = str(entry)
    segs = [s for s in entry.split(".") if s]
    pats = []

    def expand_segment(seg):
        if seg in ("*", "[]", "[*]"):
            return [("*", None)]
        out = []
        while seg:
            i = seg.find("[")
            if i == -1:
                out.append(("lit", seg))
                break
            head, rest = seg[:i], seg[i:]
            if head:
                out.append(("lit", head))
            m = re.match(r"^\[(?:\*|\d*)\]", rest)
            if not m:
                break
            out.append(("*", None))
            seg = rest[m.end():]
        return out

    expanded = []
    for s in segs:
        expanded.extend(expand_segment(s))
    pats.append(expanded)
    if "." not in entry and "*" not in entry and "[" not in entry:
        pats.append([("lit", "component"), ("lit", entry)])
    return pats


def compile_semantic_patterns(entries):
    pats = []
    for e in entries or []:
        pats.extend(expand_semantic_entry(e))
    return pats


def path_matches_semantic(segs, patterns):
    for pat in patterns:
        if len(pat) != len(segs):
            continue
        ok = True
        for (kind, val), seg in zip(pat, segs):
            if kind == "*":
                continue
            if seg != val:
                ok = False
                break
        if ok:
            return True
    return False


# --------------------------------------------------------------------------
# Walking / instantiation helpers
# --------------------------------------------------------------------------
def is_slot_obj(v):
    return isinstance(v, dict) and ("$slot" in v or "$interpolate" in v)


def instantiate(v):
    """Substitute every $slot/$interpolate with its $example (renderer-
    contract shape; the strict-instantiation view of the screen)."""
    if isinstance(v, list):
        return [instantiate(x) for x in v]
    if isinstance(v, dict):
        if "$slot" in v or "$interpolate" in v:
            return instantiate(v.get("$example"))
        return {k: instantiate(x) for k, x in v.items()}
    return v


def enum_literal(v):
    """§R10 slot-aware enum check: resolve a checked position through the
    slot lens — a $slot/$interpolate resolves to its $example, anything
    else passes through unchanged."""
    return instantiate(v) if is_slot_obj(v) else v


def scalar_str(v):
    if isinstance(v, str):
        return v
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    return None


def _has_dollar_key(v):
    if isinstance(v, dict):
        if any(k.startswith("$") for k in v):
            return True
        return any(_has_dollar_key(x) for x in v.values())
    if isinstance(v, list):
        return any(_has_dollar_key(x) for x in v)
    return False


def _path_tokens(rest):
    """'a.b[0].c' -> ['a', 'b', 0, 'c']; '' -> []."""
    out = []
    for seg in rest.split("."):
        if not seg:
            continue
        while seg:
            i = seg.find("[")
            if i == -1:
                out.append(seg)
                break
            if seg[:i]:
                out.append(seg[:i])
            m = re.match(r"^\[(\d+)\]", seg[i:])
            if not m:
                break
            out.append(int(m.group(1)))
            seg = seg[i:][m.end():]
    return out


# --------------------------------------------------------------------------
# Per-screen validation
# --------------------------------------------------------------------------
class ScreenCheck:
    """Collects errors/warns for one screen and runs the check battery."""

    def __init__(self, relpath, doc, contract, sem_patterns, states,
                 trigger_ids, canon_skips, command_registry):
        self.relpath = relpath
        self.doc = doc
        self.contract = contract
        self.sem_patterns = sem_patterns
        self.states = states
        self.trigger_ids = trigger_ids
        self.canon_skips = canon_skips
        self.command_registry = command_registry
        self.errors = []          # (json_path, message)
        self.warns = []           # (json_path, message)
        self.stats = {"slots": 0, "interpolates": 0, "volatile_hits": 0,
                      "aff_resolvable": 0, "aff_unresolvable": 0}
        self.scenario_keys_seen = set()
        self.exit = None

    def err(self, path, msg):
        self.errors.append((path, msg))

    def warn(self, path, msg):
        self.warns.append((path, msg))

    # ---- structural $-key sweep + slot grammar + semantic + volatility ----
    def check_string_leaf(self, v, p, key, in_data_block):
        """Leaf-string checks shared by dict values and array elements:
        banned 'template' substring; time-like volatile literal (§R2)."""
        if "template" in v.lower():
            self.err(p, "banned substring 'template' in a value "
                        "(plan.md §3/§11.1 guardrail)")
        if not in_data_block and is_time_like(key, v):
            self.stats["volatile_hits"] += 1
            self.err(p, f"time-like volatile literal must be a "
                        f"$slot/$interpolate (plan-2 §R2): {v!r}")

    def walk_structural(self, node, segs, in_data_block, key_ctx=""):
        if isinstance(node, str):
            # array-element leaf; key_ctx is the array's key (value-based
            # detection carries the signal for nested elements)
            self.check_string_leaf(node, ".".join(segs), key_ctx, in_data_block)
            return
        if isinstance(node, list):
            for i, v in enumerate(node):
                self.walk_structural(v, segs + [str(i)], in_data_block, key_ctx)
            return
        if not isinstance(node, dict):
            return
        if is_slot_obj(node):
            if in_data_block:
                return  # reported by the scenario/world data-block check
            self.check_slot_object(node, segs)
            return
        for k, v in node.items():
            p = ".".join(segs + [k])
            if "template" in str(k).lower():
                self.err(p, "banned substring 'template' in a key "
                            "(plan.md §3/§11.1 guardrail)")
            if k.startswith("$"):
                if segs == [] and k == "$schema":
                    continue  # schema declaration, checked separately
                self.err(p, f"unknown structural key '{k}' outside a "
                            f"$slot/$interpolate object (DSL is exactly "
                            f"$slot and $interpolate)")
                if k == "$kind" and v == "semantic":
                    self.err(p, '$kind: "semantic" is a hard error anywhere '
                                '(plan-2 §R6): rejected values cannot appear '
                                'in files')
                continue
            if path_matches_semantic(segs + [k], self.sem_patterns):
                if is_slot_obj(v):
                    self.err(p, "semantic position must be a literal; "
                                "$slot/$interpolate found (plan-2 §R3)")
                elif isinstance(v, str) and "template" in v.lower():
                    self.err(p, "banned substring 'template' in a value "
                                "(plan.md §3/§11.1 guardrail)")
                elif isinstance(v, (dict, list)):
                    # walk without volatility (semantic); template bans hold
                    self.walk_structural(v, segs + [k], True, k)
                continue
            if isinstance(v, str):
                self.check_string_leaf(v, p, k, in_data_block)
            elif isinstance(v, (dict, list)):
                child_block = in_data_block or (segs == [] and k in ("scenario", "world"))
                self.walk_structural(v, segs + [k], child_block, k)

    def check_slot_object(self, node, segs):
        p = ".".join(segs)
        ex = node.get("$example")
        key = segs[-1] if segs else ""
        if isinstance(ex, str) and is_time_like(key, ex):
            self.stats["volatile_hits"] += 1
        if "$slot" in node and "$interpolate" in node:
            self.err(p, "slot object carries both $slot and $interpolate; "
                        "exactly one form is legal")
        if "$slot" in node:
            self.stats["slots"] += 1
            self.check_slot(node, p)
        else:
            self.stats["interpolates"] += 1
            self.check_interpolate(node, p)

    def _common_slot_fields(self, node, p, allowed_keys):
        for k in node:
            if k not in allowed_keys:
                self.err(p, f"unknown $-key '{k}' in slot object (allowed: "
                            f"{sorted(allowed_keys)})")
        kind = node.get("$kind")
        if "$kind" in node:
            if kind == "semantic":
                self.err(f"{p}.$kind", '$kind: "semantic" is a hard error '
                                       'anywhere (plan-2 §R6)')
            elif kind != "instance":
                self.err(f"{p}.$kind", f'$kind must be "instance" or absent '
                                       f'(got {kind!r})')
        ex = node.get("$example")
        if "$example" not in node:
            self.err(f"{p}.$example", "$example is required (byte-golden "
                                      "for strict instantiation)")
        elif not isinstance(ex, (str, int, float, bool)):
            self.err(f"{p}.$example", f"$example must be a JSON scalar "
                                      f"(string/number/boolean; got "
                                      f"{type(ex).__name__})")
        return ex

    def resolve_binding(self, path):
        """(ok, resolved_or_reason). live.* is assertion-time data: ok but
        statically unresolved (None)."""
        prefix, _, rest = path.partition(".")
        if prefix == "live":
            return True, None
        if prefix == "scenario":
            block, name = self.doc.get("scenario"), "scenario"
        elif prefix == "context":
            block, name = self.doc.get("context"), "context"
        elif prefix == "world":
            block, name = self.doc.get("world"), "world"
        else:
            return False, f"unknown binding prefix '{prefix}'"
        if block is None:
            return False, (f"'{prefix}.*' binding but the screen carries no "
                           f"root '{prefix}' block")
        cur = block
        for seg in _path_tokens(rest):
            if isinstance(seg, int):
                if not isinstance(cur, list) or seg >= len(cur):
                    return False, (f"binding '{path}' does not resolve: "
                                   f"index [{seg}] out of range")
                cur = cur[seg]
            else:
                if not isinstance(cur, dict) or seg not in cur:
                    return False, (f"binding '{path}' does not resolve in "
                                   f"the screen's '{prefix}' block")
                cur = cur[seg]
                if prefix == "scenario":
                    self.scenario_keys_seen.add(seg)
        return True, cur

    def check_slot(self, node, p):
        ex = self._common_slot_fields(node, p, SLOT_FORM_KEYS)
        name = node.get("$slot")
        if not isinstance(name, str) or not SLOT_NAME_RE.match(name or ""):
            self.err(f"{p}.$slot", f"slot name must match ^[a-z_][a-z0-9_]*$ "
                                   f"(got {name!r})")
        frm = node.get("$from")
        if "$from" not in node:
            self.err(f"{p}.$from", "$from is required on a $slot")
        elif not isinstance(frm, str) or not BINDING_RE.match(frm):
            self.err(f"{p}.$from",
                     f"binding path {frm!r} violates the §R7 grammar "
                     f"^(context|scenario|world|live)"
                     f"(\\.[a-z_][a-z0-9_]*|\\[\\d+\\])+$")
        else:
            ok, res = self.resolve_binding(frm)
            if not ok:
                self.err(f"{p}.$from", res)
        self.check_type_constraints(node, p, ex)

    def check_interpolate(self, node, p):
        ex = self._common_slot_fields(node, p, INTERP_FORM_KEYS)
        tpl = node.get("$interpolate")
        if not isinstance(tpl, str):
            self.err(f"{p}.$interpolate", "$interpolate template must be a "
                                          "string")
            tpl = None
        b = node.get("$bindings")
        if "$bindings" not in node:
            self.err(f"{p}.$bindings", "$bindings is required on a "
                                       "$interpolate")
            b = None
        elif not isinstance(b, dict) or not all(
                isinstance(k, str) and k and isinstance(v, str)
                for k, v in b.items()):
            self.err(f"{p}.$bindings", "$bindings must be an object of "
                                       "placeholder -> binding-path strings")
            b = None
        if b is not None:
            for ph, bpath in b.items():
                if not BINDING_RE.match(bpath):
                    self.err(f"{p}.$bindings.{ph}",
                             f"binding path {bpath!r} violates the §R7 grammar")
                    continue
                ok, res = self.resolve_binding(bpath)
                if not ok:
                    self.err(f"{p}.$bindings.{ph}", res)
        if tpl is not None and b is not None:
            placeholders = set(PLACEHOLDER_RE.findall(tpl))
            unbound = placeholders - set(b)
            for ph in sorted(unbound):
                self.err(p, f"interpolate placeholder '{{{{{ph}}}}}' has no "
                            f"$bindings entry")
            for ph in sorted(set(b) - placeholders):
                self.warn(f"{p}.$bindings.{ph}",
                          f"binding '{ph}' is unused by the template")
            if ex is not None and isinstance(ex, str) and not unbound:
                self.check_interpolate_example(p, tpl, b, ex)

    def check_interpolate_example(self, p, tpl, b, ex):
        """When every binding resolves statically (scenario/context/world),
        the substituted template must equal $example."""
        resolved = {}
        for ph, bpath in b.items():
            if bpath.startswith("live."):
                return  # assertion-time data; cannot verify statically
            ok, res = self.resolve_binding(bpath)
            if not ok:
                return
            s = scalar_str(res)
            if s is None:
                return  # non-scalar binding data; skip comparison
            resolved[ph] = s
        sub = PLACEHOLDER_RE.sub(lambda m: resolved.get(m.group(1), m.group(0)), tpl)
        if sub != ex:
            self.err(f"{p}.$example",
                     f"$example {ex!r} != substituted template {sub!r}")

    def check_type_constraints(self, node, p, ex):
        typ = node.get("$type")
        pat = node.get("$pattern")
        enum = node.get("$enum")
        if "$type" in node and not isinstance(typ, str):
            self.err(f"{p}.$type", "$type must be a string when present")
        elif isinstance(typ, str) and typ in TYPE_CHECKS and ex is not None:
            if not TYPE_CHECKS[typ](ex):
                self.err(f"{p}.$example",
                         f"$example {ex!r} does not satisfy $type {typ!r}")
        if "$pattern" in node:
            if not isinstance(pat, str):
                self.err(f"{p}.$pattern", "$pattern must be a string when present")
            else:
                try:
                    rx = re.compile(pat)
                    if isinstance(ex, str) and not rx.search(ex):
                        self.err(f"{p}.$example",
                                 f"$example {ex!r} does not match $pattern "
                                 f"{pat!r}")
                except re.error as e:
                    self.err(f"{p}.$pattern", f"invalid $pattern regex: {e}")
        if "$enum" in node:
            if not isinstance(enum, list) or not all(
                    isinstance(x, (str, int, float, bool)) for x in enum):
                self.err(f"{p}.$enum", "$enum must be an array of scalars")
            elif ex is not None and ex not in enum:
                self.err(f"{p}.$example",
                         f"$example {ex!r} is not in $enum {enum!r}")

    # ---- schema / id / exit derivation ----
    def check_schema_and_id(self):
        schema = self.doc.get("$schema")
        if schema != "wireframe/v1":
            hint = " (v2 residue: run the conversion)" \
                if schema == "wireframe/v2" else ""
            self.err("$schema", f'$schema must be exactly "wireframe/v1" '
                                f'(got {schema!r}){hint}')
        sid = self.doc.get("id")
        if not isinstance(sid, str) or not sid:
            self.err("id", "id must be a non-empty string")
            return
        parts = sid.split(".")
        if len(parts) != 4:
            self.err("id", f"id must have 4 segments noun.verb.state.condition "
                           f"(got {len(parts)})")
            return
        state = parts[2]
        if state not in STATE_TO_EXIT:
            if sid in self.canon_skips:
                return  # documented canon skip owns this drift
            self.err("id", f"state segment '{state}' is not one of the six "
                           f"labels {sorted(STATE_TO_EXIT)}")
            return
        self.exit = STATE_TO_EXIT[state]

    # ---- volatility: elapsed_ms (time-like strings handled in the walk) ----
    def check_volatile_root(self):
        if "elapsed_ms" not in self.doc:
            return
        v = self.doc["elapsed_ms"]
        p = "elapsed_ms"
        if isinstance(v, dict) and "$slot" in v:
            self.stats["volatile_hits"] += 1
            return
        self.stats["volatile_hits"] += 1
        if isinstance(v, dict) and "$interpolate" in v:
            self.err(p, "root elapsed_ms must be a $slot, never a literal or "
                        "$interpolate (plan-2 §R2)")
            return
        self.err(p, f"root elapsed_ms must ALWAYS be a $slot, never a literal "
                    f"integer (plan-2 §R2); got {v!r}")

    # ---- scenario closure (reverse direction, warn-only) ----
    def check_unused_scenario_keys(self):
        scen = self.doc.get("scenario")
        if isinstance(scen, dict):
            for k in scen:
                if k not in self.scenario_keys_seen:
                    self.warn(f"scenario.{k}",
                              "scenario key referenced by no slot/bindings "
                              "(warn-only; §R8 bounds the block to what "
                              "slots reference)")

    # ---- affordances ----
    def affordance_schema(self):
        ms = (self.contract.get("_manifest") or {}).get("affordances", {}).get(
            "machine_schema", {})
        req = set(ms.get("items", {}).get("required", [])) \
            or DEFAULT_AFFORDANCE_REQUIRED
        rels = set(ms.get("items", {}).get("properties", {}).get(
            "rel", {}).get("enum", []) or []) or DEFAULT_REL_ENUM
        return req, rels, DEFAULT_RISK_ENUM

    def check_affordances(self, raw_aff):
        if self.exit != "0":
            self.err("affordances", f"affordances are exit-0-only; screen "
                                    f"exit is {self.exit} (preserved law)")
        schema_req, rel_enum, risk_enum = self.affordance_schema()
        for i, a in enumerate(raw_aff):
            p = f"affordances[{i}]"
            if not isinstance(a, dict):
                self.err(p, "affordance entry must be an object")
                continue
            missing = set(schema_req) - set(a)
            if missing:
                self.err(p, f"affordance missing required fields "
                            f"{sorted(missing)} (manifest machine_schema)")
            # §R10: enum positions are slot-aware — resolve through the
            # slot lens before the enum comparison (a $slot/$interpolate
            # is checked via its $example; anything non-scalar errors).
            rel = enum_literal(a.get("rel"))
            risk = enum_literal(a.get("risk"))
            if rel is not None and not isinstance(rel, str):
                self.err(f"{p}.rel", "rel must be a string literal or a "
                                     "$slot/$interpolate whose $example is "
                                     "a string")
            elif rel is not None and rel not in rel_enum:
                self.err(f"{p}.rel", f"rel {rel!r} not in {sorted(rel_enum)}")
            if risk is not None and not isinstance(risk, str):
                self.err(f"{p}.risk", "risk must be a string literal or a "
                                      "$slot/$interpolate whose $example is "
                                      "a string")
            elif risk is not None and risk not in risk_enum:
                self.err(f"{p}.risk", f"risk {risk!r} not in "
                                      f"{sorted(risk_enum)}")
            if "requires_intent" in a:
                if risk != "mutating":
                    self.err(f"{p}.requires_intent",
                             f"requires_intent is a derived field and may "
                             f"only accompany risk=='mutating' (got "
                             f"risk=={risk!r}); manifest machine_schema "
                             f"carries no requires_intent")
                elif not isinstance(a["requires_intent"], bool):
                    self.err(f"{p}.requires_intent",
                             "requires_intent must be a boolean when present")
            cmd = a.get("command")
            inst = instantiate(cmd) if is_slot_obj(cmd) else cmd
            s = scalar_str(inst)
            if s is None:
                self.err(f"{p}.command",
                         "affordance command must be a string or a "
                         "$slot/$interpolate with a scalar $example")
                continue
            if s in self.command_registry:
                self.stats["aff_resolvable"] += 1
            else:
                self.stats["aff_unresolvable"] += 1
                self.warn(f"{p}.command",
                          f"affordance command {s!r} matches no command-bearing "
                          f"$slot/$interpolate $example in the validated set "
                          f"(unresolvable; counted, not an error)")

    # ---- attention affordances share the machine schema ----
    def check_attention(self, att):
        if not isinstance(att, dict):
            return
        schema_req, rel_enum, risk_enum = self.affordance_schema()
        for arr in ("top", "suppressed"):
            for i, item in enumerate(att.get(arr) or []):
                if not isinstance(item, dict):
                    continue
                aff = item.get("affordance")
                if not isinstance(aff, dict):
                    continue
                p = f"attention.{arr}[{i}].affordance"
                missing = set(schema_req) - set(aff)
                if missing:
                    self.err(p, f"affordance missing required fields "
                                f"{sorted(missing)}")
                rel = enum_literal(aff.get("rel"))
                risk = enum_literal(aff.get("risk"))
                if rel is not None and not isinstance(rel, str):
                    self.err(f"{p}.rel", "rel must be a string literal or a "
                                         "$slot/$interpolate whose $example "
                                         "is a string")
                elif rel is not None and rel not in rel_enum:
                    self.err(f"{p}.rel", f"rel {rel!r} not in "
                                         f"{sorted(rel_enum)}")
                if risk is not None and not isinstance(risk, str):
                    self.err(f"{p}.risk", "risk must be a string literal or "
                                          "a $slot/$interpolate whose "
                                          "$example is a string")
                elif risk is not None and risk not in risk_enum:
                    self.err(f"{p}.risk", f"risk {risk!r} not in "
                                          f"{sorted(risk_enum)}")

    # ---- trailer law ----
    def check_trailer(self):
        if "next_action" in self.doc:
            self.err("next_action", "root next_action must never appear on a "
                                    "screen (the machine envelope derives it; "
                                    "wireframe-structure.md §6.1.1)")
        tr = self.doc.get("trailer")
        if tr is None:
            if self.trigger_ids and self.doc.get("id") in self.trigger_ids:
                self.err("trailer", "screen id is named in _triggers.json; "
                                    "trailer present iff the trigger says so")
            return
        if not isinstance(tr, dict):
            self.err("trailer", "trailer must be an object")
            return
        if self.trigger_ids is None:
            self.warn("trailer", "_triggers.json unreadable; presence law "
                                 "not enforced")
        elif self.doc.get("id") not in self.trigger_ids:
            self.err("trailer", f"trailer present but screen id "
                                f"{self.doc.get('id')!r} is not named in "
                                f"_triggers.json (trailer law)")
        prompt = tr.get("prompt")
        if is_slot_obj(prompt):
            self.err("trailer.prompt", "trailer.prompt is a semantic literal "
                                       "(plan-2 §R3); $slot/$interpolate found")
        inst = instantiate(tr)
        props = (self.contract.get("_manifest_trailer") or {}).get(
            "properties", {})
        required = (self.contract.get("_manifest_trailer") or {}).get(
            "required", ["prompt", "reason", "serve"])
        for req in required:
            if req not in inst:
                self.err(f"trailer.{req}",
                         f"trailer missing required field '{req}' "
                         f"(manifest machine_schema)")
        pat = props.get("prompt", {}).get("pattern")
        if isinstance(inst.get("prompt"), str) and pat:
            try:
                if not re.search(pat, inst["prompt"]):
                    self.err("trailer.prompt",
                             f"prompt {inst['prompt']!r} does not match "
                             f"machine_schema pattern {pat!r}")
            except re.error:
                pass
        serve_enum = props.get("serve", {}).get("enum")
        if serve_enum and inst.get("serve") is not None \
                and inst["serve"] not in serve_enum:
            self.err("trailer.serve", f"serve {inst['serve']!r} not in "
                                      f"{serve_enum} (manifest machine_schema)")

    # ---- isolated markers (plan-2 §R9) ----
    def check_isolated(self):
        sid = self.doc.get("id", "")
        has_iso = "isolated" in self.doc
        has_reason = "isolated_reason" in self.doc
        if not (has_iso or has_reason):
            return
        if not sid.startswith("sys.shim."):
            self.err("isolated" if has_iso else "isolated_reason",
                     f"isolated markers are carried only on sys.shim.* "
                     f"fixtures (plan-2 §R9); found on {sid!r}")
            return
        if self.doc.get("isolated") is not True:
            self.err("isolated", "isolated must be boolean true")
        r = self.doc.get("isolated_reason")
        if not isinstance(r, str) or not r.strip():
            self.err("isolated_reason",
                     "isolated_reason must be a non-empty string")

    # ---- archetype structural checks (§6.1 Component law) ----
    def check_archetype(self):
        arch = self.doc.get("archetype")
        if arch not in ("diagnostic", "tree", "receipt", "document"):
            self.err("archetype",
                     f"archetype {arch!r} not in the closed set "
                     f"{{diagnostic, tree, receipt, document}}")
            return
        if self.exit is None:
            return  # id/exit errors already reported (or canon-skipped)
        skip_derivation = self.doc.get("id") in self.canon_skips
        if not skip_derivation and arch not in EXIT_ARCHETYPES[self.exit]:
            self.err("archetype",
                     f"exit {self.exit} screens must be "
                     f"{sorted(EXIT_ARCHETYPES[self.exit])}; got {arch!r} "
                     f"(state taxonomy)")
        comp = self.doc.get("component")
        if not isinstance(comp, dict):
            self.err("component", "component must be an object")
            return
        inst = instantiate(comp)
        if arch == "diagnostic":
            self.check_diagnostic(comp, inst)
        elif arch == "tree":
            self.check_tree(inst)
        elif arch == "receipt":
            self.check_receipt(inst)
        elif arch == "document":
            self.check_document(inst)
        if not skip_derivation:
            self.check_domain_taxonomy(inst)

    def check_diagnostic(self, comp, inst):
        for k in ("domain", "culprit", "remedy"):
            v = inst.get(k)
            if not isinstance(v, str) or not v:
                self.err(f"component.{k}",
                         f"diagnostic components carry {k} as a non-empty "
                         f"string (§6.1 Component law)")
        for k in ("rule", "layer"):
            if k in comp and is_slot_obj(comp[k]):
                self.err(f"component.{k}",
                         f"rule/layer are semantic literals where present "
                         f"(§6.1); $slot/$interpolate found")

    def check_tree(self, inst):
        for k in ("title", "root"):
            if not isinstance(inst.get(k), str):
                self.err(f"component.{k}",
                         f"tree components carry {k} as a string (§6.1)")
        nodes = inst.get("nodes")
        if not isinstance(nodes, list):
            self.err("component.nodes",
                     "tree components carry nodes as an array (§6.1)")
            return
        self.check_tree_nodes(nodes, "component.nodes")

    def check_tree_nodes(self, nodes, p):
        for i, n in enumerate(nodes):
            q = f"{p}[{i}]"
            if not isinstance(n, dict) or not isinstance(n.get("label"), str) \
                    or not isinstance(n.get("children"), list):
                self.err(q, "tree nodes are {label: string, children: array} "
                            "recursing (§6.1)")
                continue
            self.check_tree_nodes(n["children"], q + ".children")

    def check_receipt(self, inst):
        # Shape law mirrors the committed renderer contract (wireframe.html
        # renderReceipt): a `groups` array, OR the flat shape (top-level
        # `fields` object / `title`) which the renderer lifts into one
        # synthetic group; top-level `lines` render as an extra section.
        # 3-b finalization of 3-c's in-flight reconciliation draft: keep
        # validating every key that IS present, in both shapes.
        groups = inst.get("groups")
        flat = inst.get("fields") is not None or inst.get("title") is not None \
            or inst.get("lines") is not None
        if groups is None and not flat:
            self.err("component.groups",
                     "receipt components carry groups ({title?, fields?, "
                     "lines?}), the flat fields/title shape the renderer "
                     "lifts, or at least a top-level `lines` section — "
                     "anything renderReceipt renders (wireframe.html, §6.1)")
        elif groups is not None and not isinstance(groups, list):
            self.err("component.groups",
                     "receipt groups must be an array when present (§6.1)")
        if isinstance(groups, list):
            for i, g in enumerate(groups):
                q = f"component.groups[{i}]"
                if not isinstance(g, dict):
                    self.err(q, "receipt group must be an object")
                    continue
                if not any(k in g for k in ("title", "fields", "lines")):
                    self.err(q, "receipt group carries none of title/fields/lines")
                if "fields" in g and not isinstance(g["fields"], dict):
                    self.err(q + ".fields",
                             "group fields must be an ordered key-value map (§6.1)")
                if "lines" in g and (not isinstance(g["lines"], list)
                                     or not all(isinstance(x, str) for x in g["lines"])):
                    self.err(q + ".lines",
                             "group lines must be an array of strings (§6.1)")
                if "title" in g and g["title"] is not None \
                        and not isinstance(g["title"], str):
                    self.err(q + ".title", "group title must be a string or null")
        fields = inst.get("fields")
        if fields is not None and not isinstance(fields, dict):
            self.err("component.fields",
                     "flat receipt `fields` must be an object (the renderer "
                     "lifts it into one group; wireframe.html renderReceipt)")
        lines = inst.get("lines")
        if lines is not None and (not isinstance(lines, list)
                                  or not all(isinstance(x, str) for x in lines)):
            self.err("component.lines",
                     "top-level receipt `lines` must be an array of strings "
                     "(the renderer renders it as an extra section; §6.1)")

    def check_document(self, inst):
        if not isinstance(inst.get("header_badge"), str):
            self.err("component.header_badge",
                     "document components carry header_badge as a string (§6.1)")
        body = inst.get("body")
        if not isinstance(body, list) or not all(
                isinstance(x, str) for x in body):
            self.err("component.body",
                     "document body must be an array of prose strings (§6.1)")
        pag = inst.get("pagination")
        if pag is not None:
            if not isinstance(pag, dict):
                self.err("component.pagination",
                         "pagination must be the keyset envelope object")
            else:
                if not isinstance(pag.get("items"), list):
                    self.err("component.pagination.items",
                             "pagination envelope carries items (§6.1.2)")
                nc = pag.get("next_cursor")
                if not (nc is None or isinstance(nc, str)):
                    self.err("component.pagination.next_cursor",
                             "pagination envelope carries next_cursor "
                             "(§6.1.2; string cursor, or null on the "
                             "terminal page — 3-c reconciliation with the "
                             "on-disk fixture)")
                if not isinstance(pag.get("has_more"), bool):
                    self.err("component.pagination.has_more",
                             "pagination envelope carries has_more (§6.1.2)")

    def check_domain_taxonomy(self, inst):
        dom = inst.get("domain")
        if self.exit == "0":
            if dom:
                self.err("component.domain",
                         f"exit-0 screen carries domain {dom!r} (canon: "
                         f"exit 0 carries no domain)")
            return
        allowed = set((self.states.get(self.exit) or {}).get("domains", []))
        if dom and allowed and dom not in allowed:
            self.err("component.domain",
                     f"domain {dom!r} not in _states.json exit-{self.exit} "
                     f"domains {sorted(allowed)}")

    # ---- driver ----
    def run(self):
        if not isinstance(self.doc, dict):
            self.err("$", "screen must be a JSON object")
            return
        self.check_schema_and_id()
        for name in ("scenario", "world"):
            block = self.doc.get(name)
            if isinstance(block, dict):
                for k, v in block.items():
                    if is_slot_obj(v) or _has_dollar_key(v):
                        self.err(f"{name}.{k}",
                                 f"'{name}' block is binding data (plan.md "
                                 f"§5); $-keys are not legal here")
        self.check_volatile_root()
        self.walk_structural(self.doc, [], False)
        self.check_unused_scenario_keys()
        if isinstance(self.doc.get("affordances"), list):
            self.check_affordances(self.doc["affordances"])
        if "attention" in self.doc:
            self.check_attention(self.doc.get("attention"))
        self.check_trailer()
        self.check_isolated()
        self.check_archetype()


# --------------------------------------------------------------------------
# Multi-file driver
# --------------------------------------------------------------------------
def collect_files(paths):
    files = []
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            files.extend(sorted(pp.rglob("*.json")))
        elif pp.is_file() and pp.suffix == ".json":
            files.append(pp)
        else:
            print(f"  [SKIP] {p}: not a .json file or directory", file=sys.stderr)
    return files


def collect_command_registry(docs):
    """command-bearing $slot/$interpolate $examples across the validated
    set: the root 'command' and any 'command' under 'component' (the
    modeled invocations). Affordance commands — root affordances[] and
    attention.*.affordance — are deliberately EXCLUDED, else every
    affordance would attest itself."""
    reg = set()

    def add(v):
        s = scalar_str(instantiate(v) if is_slot_obj(v) else v)
        if s is not None:
            reg.add(s)

    for doc in docs:
        if not isinstance(doc, dict):
            continue
        if "command" in doc:
            add(doc["command"])
        comp = doc.get("component")
        if isinstance(comp, dict):
            for v in _find_command_values(comp):
                add(v)
    return reg


def _find_command_values(node):
    if isinstance(node, list):
        for x in node:
            yield from _find_command_values(x)
    elif isinstance(node, dict):
        if is_slot_obj(node):
            return  # slot objects are yielded by their 'command' parent only
        for k, v in node.items():
            if k == "command":
                yield v
            elif isinstance(v, (dict, list)):
                yield from _find_command_values(v)


def run(paths, verbose=False, want_summary=False):
    contract, note = load_manifest_contract()
    manifest, _ = load_json(WIREFRAME / "manifest.json")
    oc = (manifest or {}).get("output_contract", {})
    contract["_manifest"] = oc
    contract["_manifest_trailer"] = oc.get("trailer", {}).get("machine_schema", {})
    sem_patterns = compile_semantic_patterns(
        contract.get("semantic_positions")
        or DEFAULT_SLOT_CONTRACT["semantic_positions"])
    states = load_states()
    trigger_ids, trig_err = load_trigger_ids()
    canon_skips = load_canon_fixture_skips()

    files = collect_files(paths)
    if not files:
        print("[FAIL] no screens found to validate", file=sys.stderr)
        return 1, {}

    docs, parse_errors = [], []
    for f in files:
        d, err = load_json(f)
        if d is None:
            parse_errors.append((f, err))
        else:
            docs.append((f, d))

    registry = collect_command_registry([d for _, d in docs])

    if note:
        print(f"  [NOTE] {note}", file=sys.stderr)
    if trig_err:
        print(f"  [NOTE] _triggers.json unreadable ({trig_err}); trailer "
              f"presence law degraded", file=sys.stderr)

    total_errors = 0
    total_warns = 0
    stats = {"screens": 0, "slots": 0, "interpolates": 0, "volatile_hits": 0,
             "aff_resolvable": 0, "aff_unresolvable": 0,
             "parse_errors": len(parse_errors)}
    files_with_errors = 0
    seen_lines = set()

    def relpath(f):
        try:
            return str(f.relative_to(ROOT))
        except ValueError:
            return str(f)

    for f, err in parse_errors:
        print(f"  [FAIL] {relpath(f)} :: $ :: malformed JSON: {err}",
              file=sys.stderr)
        total_errors += 1
        files_with_errors += 1

    for f, d in docs:
        rel = relpath(f)
        chk = ScreenCheck(rel, d, contract, sem_patterns, states,
                          trigger_ids, canon_skips, registry)
        try:
            chk.run()
        except Exception as exc:  # never abort the whole sweep on one file
            chk.err("$", f"validator internal error while checking this "
                         f"screen ({type(exc).__name__}: {exc}); report as "
                         f"a bug if the file is conformant v1")
        stats["screens"] += 1
        for k in ("slots", "interpolates", "volatile_hits",
                  "aff_resolvable", "aff_unresolvable"):
            stats[k] += chk.stats[k]
        total_warns += len(chk.warns)
        if chk.errors:
            files_with_errors += 1
            total_errors += len(chk.errors)
            for p, msg in chk.errors:
                line = f"  [FAIL] {rel} :: {p or '$'} :: {msg}"
                if line not in seen_lines:
                    seen_lines.add(line)
                    print(line, file=sys.stderr)
        elif verbose:
            print(f"  [PASS] {rel} :: {chk.stats['slots']} slots, "
                  f"{chk.stats['interpolates']} interpolates, "
                  f"{chk.stats['volatile_hits']} volatile hits, "
                  f"{len(chk.warns)} warn(s)")
        for p, msg in chk.warns:
            print(f"  [WARN] {rel} :: {p} :: {msg}", file=sys.stderr)

    if want_summary:
        print(f"summary: screens={stats['screens']} slots={stats['slots']} "
              f"interpolates={stats['interpolates']} "
              f"volatile_hits={stats['volatile_hits']} "
              f"affordance_attestations={stats['aff_resolvable']} resolvable / "
              f"{stats['aff_unresolvable']} unresolvable (warned) "
              f"warns={total_warns} parse_errors={stats['parse_errors']}")

    if total_errors:
        print(f"[FAIL] wireframe/v1 validation: {stats['screens']} screens, "
              f"{total_errors} error(s) across {files_with_errors} file(s), "
              f"{total_warns} warn(s).", file=sys.stderr)
        return 1, stats
    print(f"[PASS] wireframe/v1 validation: {stats['screens']} screens, "
          f"0 errors, {total_warns} warn(s).")
    return 0, stats


def main(argv):
    verbose = False
    want_summary = False
    paths = []
    for a in argv:
        if a in ("-v", "--verbose"):
            verbose = True
        elif a in ("-s", "--summary"):
            want_summary = True
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            paths.append(a)
    if not paths:
        paths = [str(SCREENS)]
    print("Validating wireframe/v1 screens...")
    code, _ = run(paths, verbose=verbose, want_summary=want_summary)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
