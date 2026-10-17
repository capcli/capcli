#!/usr/bin/env python3
"""convert_wireframe_v1.py — deterministic wireframe/v2 -> wireframe/v1 screen converter.

Task 3-c workhorse (plan-2 §R14.3, diff-patches §2). stdlib only, python3.

Modes:
  (default)              convert screens under cans/artifacts/wireframe/screens/
  --files <f> [f ...]    convert specific screen files
  --embeds <md>          convert the 14 §5 fixture embeds of wireframe-structure.md
                         in lockstep (§R12: embeds are indexes, never originate;
                         the screen fixture wins any conflict; only §5 is touched)
  --states               regenerate _states.json domain_fields from v1 screens (§R13)
  --check                idempotency check: reconvert and report any drift
  --stats                print measured counts after a conversion run

Conversion rules per screen (§R2/§R3/§R4/§R5/§R6/§R7/§R8/§R9):
  * "$schema": "wireframe/v2" -> "wireframe/v1".
  * Root `scenario` block (§R8) holding ONLY the keys the screen's own slots
    reference, extracted from tree-root / target / command data. Keys are
    lower_snake and descriptive. Extraction order: root-derived, target-derived,
    command-derived (matches diff-patches §2.1 and §2.2 exemplars).
  * Slot every instance literal (§R3 "everything else slots"), current literal
    as $example everywhere. Never slotted (semantic, §R3/§R4/§R9): $schema, id,
    archetype, rule, domain, layer, remedy, context.env, context.tier,
    context.trust, trailer.prompt, attention top[].class, isolated,
    isolated_reason. No $kind key is emitted (§R6: optional and absent).
  * Volatility (§R2): root elapsed_ms -> {"$slot":"elapsed_ms","$from":
    "live.elapsed_ms","$type":"integer","$example":N} on every screen;
    time-like component strings (durations, clock times, windows) are slotted.
  * `target` (311 screens; skipped on the 9 target-less screens, §R5) binds
    scenario.<key>; `command` becomes $interpolate over its variable parts;
    `audit_op` -> live.audit_op; affordance/attention-affordance commands
    become $interpolate.
  * suspended_frame slots as frame_id (live.frame_id) and component `verb`
    slots as api_verb (live.api_verb) per diff-patches §2.1; tree node labels
    use positional names n0 / n0c0 ... bound live.<verb>.nodes[i]...label per
    diff-patches §2.2.
  * Binding paths match the §R7 grammar; display-label map keys are slugified
    to lower_snake segments so every path stays in-grammar.
  * isolated / isolated_reason carried through untouched (§R9).
  * Output format preserves each file's existing style: single-line compact
    (sort_keys, ","/":") stays single-line sorted; pretty files keep indent 2
    and author key order (scenario inserted after `id`); unicode escaping
    style and trailing newline preserved per file.

Idempotent: converting a wireframe/v1 screen leaves it byte-identical.
"""

import argparse
import json
import os
import re
import sys

WIREFRAME_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cans", "artifacts", "wireframe",
)
SCREENS_DIR = os.path.join(WIREFRAME_ROOT, "screens")
STATES_PATH = os.path.join(WIREFRAME_ROOT, "_states.json")
STRUCTURE_PATH = os.path.join(WIREFRAME_ROOT, "wireframe-structure.md")

SCHEMA_V2 = "wireframe/v2"
SCHEMA_V1 = "wireframe/v1"

# Semantic positions — never slotted (plan-2 §R3 closed list + §R4 + §R9).
SEMANTIC_ROOT_KEYS = {"$schema", "id", "archetype", "isolated", "isolated_reason"}
SEMANTIC_CONTEXT_KEYS = {"env", "tier", "trust"}
SEMANTIC_TRAILER_KEYS = {"prompt"}
SEMANTIC_ATTENTION_KEYS = {"class"}

DIAGNOSTIC_CORE = {"domain", "rule", "layer", "culprit", "remedy"}

# §R2 volatility detector (reporting): durations, clock times, windows.
TIME_PATTERNS = [
    re.compile(r"\b\d{1,2}:\d{2}(:\d{2})?(\s*(UTC|utc))?\b"),
    re.compile(r"\bin\s+\d+(\.\d+)?\s*(ms|s|m|h|d)\b(?:\s*(and\s+)?\d+\s*(ms|s|m|h|d)\b)*"),
    re.compile(r"\b\d+(\.\d+)?\s?(ms|s|m|h|d)\b(?!\w)"),
]
# component keys whose whole value is a time-like cite even without a unit hit
TIME_LIKE_KEYS = {
    "next_fire", "last_fire", "reset_at", "expires_at", "issued_at",
    "enqueued_at", "waited", "uptime", "ttl", "ttl_remaining", "duration",
    "window", "since",
}

BOUND = r"(?<![A-Za-z0-9_:@/\-])"
BOUND_END = r"(?![A-Za-z0-9_:@/\-])"


def slugify(name):
    """Map an arbitrary JSON key to a lower_snake binding/slot name."""
    s = re.sub(r"[^0-9a-zA-Z]+", "_", str(name)).lower()
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "k"
    if not re.match(r"^[a-z_]", s):
        s = "k_" + s
    return s


def time_like(value, key=None):
    """True when a string value is or embeds a time-like span (§R2)."""
    if not isinstance(value, str):
        return False
    if key in TIME_LIKE_KEYS:
        return True
    return any(p.search(value) for p in TIME_PATTERNS)


class ScreenConverter:
    """Converts one v2 screen dict to a v1 screen dict (pure, deterministic)."""

    def __init__(self):
        self.stats = {"slots": 0, "interpolates": 0, "empty_interpolates": 0,
                      "timelike": 0, "scenario_refs": set()}

    def reset(self):
        self.scen = {}                 # scenario key -> value (insertion-ordered)
        self.used_slot_names = set()   # per-screen slot-name uniqueness
        self.elem_counters = {}        # per-array-key positional counters
        for k in ("slots", "interpolates", "empty_interpolates", "timelike"):
            self.stats[k] = 0
        self.stats["scenario_refs"] = set()

    def measure_timelike(self, screen):
        """§R2 pre-conversion count of time-like component string values
        (semantic positions excluded; remedy is deterministic per §R4)."""
        n = 0

        def walk(v, key=None, semantic=False):
            nonlocal n
            if isinstance(v, dict):
                for k, x in v.items():
                    walk(x, k, semantic or k in ("rule", "domain", "layer", "remedy"))
            elif isinstance(v, list):
                for x in v:
                    walk(x, key, semantic)
            elif isinstance(v, str) and not semantic and time_like(v, key):
                n += 1

        walk(screen.get("component") or {})
        return n

    # ------------------------------------------------------------- scenario --
    def add_scen(self, key, value):
        if key in self.scen and self.scen[key] != value:
            i = 2
            while f"{key}_{i}" in self.scen:
                i += 1
            key = f"{key}_{i}"
        self.scen[key] = value
        return key

    def ref_scen(self, key):
        self.stats["scenario_refs"].add(key)

    @staticmethod
    def component_key_for_value(screen, value):
        """First component map key (depth-first) whose scalar value == value."""
        comp = screen.get("component") or {}

        def walk(v):
            if isinstance(v, dict):
                for k, x in v.items():
                    if isinstance(value, str) and x == value:
                        return k
                    found = walk(x)
                    if found:
                        return found
            elif isinstance(v, list):
                for x in v:
                    found = walk(x)
                    if found:
                        return found
            return None

        return walk(comp)

    def root_scenario_keys(self, screen):
        """Scenario keys derived from a tree root (session + root intent)."""
        if screen.get("archetype") != "tree":
            return []
        root = (screen.get("component") or {}).get("root")
        if not isinstance(root, str):
            return []
        keys = []
        m = re.match(r'^(ses_\w+)\s+\S+\s+"(.+)"$', root)
        if m:
            self.add_scen("session_id", m.group(1))
            keys.append("session_id")
            self.add_scen("root_intent", m.group(2))
            keys.append("root_intent")
            return keys
        m = re.search(r"\bses_\w+\b", root)
        if m:
            self.add_scen("session_id", m.group(0))
            keys.append("session_id")
        return keys

    def target_scenario_keys(self, screen):
        """Scenario keys derived from the target (§R5/§R8). [] when absent."""
        target = screen.get("target")
        if not isinstance(target, str) or not target:
            return []
        keys = []

        def put(key, value=None):
            self.add_scen(key, target if value is None else value)
            keys.append(key)

        m = re.match(r"^cap://([^@]+)@(\d+)$", target)
        if m:
            put("routine_urp")
            put("routine_name", m.group(1))
            put("routine_version", int(m.group(2)))
            return keys
        m = re.match(r"^cap://(.+)$", target)
        if m:
            put("routine_urp")
            if re.match(r"^[a-z_][a-z0-9_.]*$", m.group(1)) and "@" not in m.group(1):
                put("routine_name", m.group(1))
            return keys
        m = re.match(r"^([a-z]+)://", target)
        if m:
            key = {
                "pack": "pack_urp", "ws": "ws_urp", "env": "env_urp",
                "doc": "doc_urp", "db": "db_urp", "schema": "schema_urp",
                "audit": "audit_urp", "ask": "ask_urp", "quota": "quota_urp",
                "vault": "vault_urp", "policy": "policy_urp",
                "plugin": "plugin_urp", "http": "url", "https": "url",
                "hub": "hub_addr", "tcp": "tcp_addr",
            }.get(m.group(1), m.group(1) + "_urp")
            put(key)
            return keys
        if re.match(r"^ses_", target):
            put("session_id"); return keys
        if re.match(r"^op_", target):
            verb = screen["id"].split(".")[1] if "." in screen["id"] else ""
            put("trace_op" if verb == "trace" else "op_id"); return keys
        if re.match(r"^ask_", target):
            put("ask_id"); return keys
        if re.match(r"^agt_", target):
            put("agent_id"); return keys
        if re.match(r"^bnd_", target):
            put("binding_id"); return keys
        if re.match(r"^evt_", target):
            put("event_id"); return keys
        if re.match(r"^(frame|frm|task)_", target):
            put("frame_id"); return keys
        if re.match(r"^snap", target):
            put("snapshot_id"); return keys
        if target.startswith("CAPCLI_SECRET"):
            put("secret_ref"); return keys
        if re.match(r"^[\w.\-]+:[\w.\-]+$", target) and not target.startswith(("git:", "user:")):
            put("db_key"); return keys                      # orders:ORD-10
        if target.startswith("user:"):
            put("principal"); return keys
        if target.startswith("git:"):
            put("git_ref"); return keys
        m = re.match(r"^(\w+)@(\w+)$", target)              # dispatch_order@4
        if m:
            put("routine_ref")
            put("routine_name", m.group(1))
            put("routine_version", int(m.group(2)) if m.group(2).isdigit() else m.group(2))
            return keys
        if target.endswith(".db"):
            put("db_path"); return keys
        if target.startswith("/"):
            put("target_path"); return keys
        # plain word: reuse a component map key whose value equals the target,
        # else slugify the target itself (descriptive lower_snake).
        key = self.component_key_for_value(screen, target) or slugify(target)
        put(key)
        return keys

    def command_scenario_keys(self, screen):
        """Scenario keys derived from -p / -m request parameters."""
        cmd = screen.get("command")
        if not isinstance(cmd, str):
            return []
        keys = []
        for m in re.finditer(r'(?:^|\s)-p(?:\s+|=)([A-Za-z_][\w.\-]*)=("[^"]*"|\S+)', cmd):
            k, v = m.group(1), m.group(2)
            if v.startswith('"') and v.endswith('"') and len(v) >= 2:
                v = v[1:-1]
            keys.append(self.add_scen(slugify(k), v))
        m = re.search(r'(?:^|\s)-m\s+("[^"]*"|\S+)', cmd)
        if m:
            v = m.group(1)
            if v.startswith('"') and v.endswith('"') and len(v) >= 2:
                v = v[1:-1]
            keys.append(self.add_scen("intent", v))
        return keys

    # ---------------------------------------------------------- interpolation --
    def build_interpolate(self, s):
        """$interpolate for a string embedding scenario tokens; None if none."""
        tmpl = s
        bindings = {}

        def replace_value(value, name, binding):
            nonlocal tmpl
            if not isinstance(value, str) or not value or len(value) > len(s):
                return False
            pat = re.compile(BOUND + re.escape(value) + BOUND_END)
            if not pat.search(tmpl):
                return False
            tmpl = pat.sub("{{" + name + "}}", tmpl)
            bindings[name] = binding
            return True

        # 1. the dispatched target value (whole token)
        if "target_key" in self.scen:
            tkey = self.scen["target_key"]
            replace_value(self.scen[tkey], tkey, "scenario." + tkey)
        # 2. routine_name@routine_version composite token
        if "routine_name" in self.scen and "routine_version" in self.scen:
            esc = (re.escape(str(self.scen["routine_name"])) + r"@" +
                   re.escape(str(self.scen["routine_version"])))
            pat = re.compile(BOUND + esc + BOUND_END)
            if pat.search(tmpl):
                tmpl = pat.sub("{{routine_name}}@{{routine_version}}", tmpl)
                bindings["routine_name"] = "scenario.routine_name"
                bindings["routine_version"] = "scenario.routine_version"
                self.ref_scen("routine_name")
                self.ref_scen("routine_version")
        # 3. remaining scenario values, longest first
        for key, val in sorted(self.scen.items(), key=lambda kv: -len(str(kv[1]))):
            if key == "target_key":
                continue
            if key in ("routine_name", "routine_version"):
                continue
            if "scenario." + key in bindings.values():
                continue
            if replace_value(val, key, "scenario." + key):
                self.ref_scen(key)
        # 4. frame-like token -> live.frame_id, only alongside scenario tokens,
        #    and only when exactly one distinct frame value remains
        frame_pat = re.compile(r"\b(?:frame|frm|task)_[0-9a-z]+\b")
        found = set(frame_pat.findall(tmpl))
        if bindings and len(found) == 1:
            tmpl = frame_pat.sub("{{frame_id}}", tmpl)
            bindings["frame_id"] = "live.frame_id"

        if not bindings:
            return None
        # reorder bindings by first occurrence in the template (exemplar style)
        ordered = {}
        for name in sorted(bindings, key=lambda nm: tmpl.index("{{" + nm + "}}")):
            ordered[name] = bindings[name]
        self.stats["interpolates"] += 1
        return {"$interpolate": tmpl, "$bindings": ordered, "$example": s}

    # ------------------------------------------------------------------ slots --
    def slot(self, name, from_path, example, vtype=None):
        while name in self.used_slot_names:
            m = re.match(r"^(.*)_(\d+)$", name)
            name = f"{m.group(1)}_{int(m.group(2)) + 1}" if m else name + "_2"
        self.used_slot_names.add(name)
        obj = {"$slot": name, "$from": from_path}
        if vtype:
            obj["$type"] = vtype
        obj["$example"] = example
        self.stats["slots"] += 1
        return obj

    def convert_string(self, s, live_path, slot_base, slot_name=None):
        """§R3 string rule: whole-equal scenario -> scenario slot;
        embedded scenario tokens -> $interpolate; else whole live slot."""
        for key, val in self.scen.items():
            if key != "target_key" and s == val:
                self.ref_scen(key)
                return self.slot(key, "scenario." + key, s)
        interp = self.build_interpolate(s)
        if interp is not None:
            return interp
        name = slugify(slot_name or slot_base)
        return self.slot(name, live_path, s)

    def convert_scalar(self, v, live_path, slot_base, slot_name=None):
        if isinstance(v, str):
            return self.convert_string(v, live_path, slot_base, slot_name)
        if isinstance(v, bool):
            return self.slot(slugify(slot_name or slot_base), live_path, v,
                             vtype="boolean")
        if isinstance(v, int):
            return self.slot(slugify(slot_name or slot_base), live_path, v,
                             vtype="integer")
        if isinstance(v, float):
            return self.slot(slugify(slot_name or slot_base), live_path, v,
                             vtype="number")
        return v  # None / containers pass through untouched

    def convert_element(self, x, live_path, base_key):
        """Scalar element of a string array: positional slot name (line_N)."""
        if isinstance(x, str):
            for key, val in self.scen.items():
                if key != "target_key" and x == val:
                    self.ref_scen(key)
                    return self.slot(key, "scenario." + key, x)
            interp = self.build_interpolate(x)
            if interp is not None:
                return interp
            n = self.elem_counters.get(base_key, 0)
            self.elem_counters[base_key] = n + 1
            base = slugify(base_key) or "item"
            return self.slot(f"{base}_{n}", live_path, x)
        return self.convert_scalar(x, live_path, base_key)

    def special_flat_slot(self, key, value):
        """Exemplar §2.1 renames: suspended_frame -> frame_id, verb -> api_verb."""
        if key == "suspended_frame":
            return self.slot("frame_id", "live.frame_id", value)
        if key == "verb":
            return self.slot("api_verb", "live.api_verb", value)
        return None

    # ------------------------------------------------------------ tree labels --
    @staticmethod
    def tree_label_name(path):
        """nodes[0].children[1].label -> n0c1 (diff-patches §2.2)."""
        idx = re.findall(r"\[(\d+)\]", path)
        if not idx:
            return None
        return "n" + idx[0] + "".join(f"c{i}" for i in idx[1:])

    # ------------------------------------------------------------- walk logic --
    def convert_component(self, comp, tree_root):
        live_root = "live." + tree_root if tree_root else "live"

        def seg(k):
            """Binding-path segment: lower_snake per the §R7 grammar."""
            return k if re.match(r"^[a-z_][a-z0-9_]*$", str(k)) else slugify(k)

        def walk(v, path, base_key):
            if isinstance(v, dict):
                out = {}
                for k, x in v.items():
                    if k in ("rule", "domain", "layer", "remedy"):
                        out[k] = x          # semantic — never slotted (§R3/§R4)
                        continue
                    kp = (path + "." + seg(k) if path else seg(k))
                    if k in ("suspended_frame", "verb") and isinstance(x, str):
                        sp = self.special_flat_slot(k, x)
                        out[k] = sp if sp is not None else self.convert_scalar(
                            x, f"{live_root}.{kp}", k)
                        continue
                    out[k] = walk(x, kp, k)
                return out
            if isinstance(v, list):
                out = []
                for i, x in enumerate(v):
                    lp = f"{live_root}.{path}[{i}]"
                    if isinstance(x, (str, int, float, bool)):
                        out.append(self.convert_element(x, lp, base_key))
                    else:
                        out.append(walk(x, f"{path}[{i}]", base_key))
                return out
            if isinstance(v, (str, int, float, bool)):
                if base_key == "label":
                    # tree node labels: positional whole-value live slots,
                    # never interpolated (diff-patches §2.2)
                    name = self.tree_label_name(path) or slugify(base_key)
                    return self.slot(name, f"{live_root}.{path}", v)
                return self.convert_scalar(v, f"{live_root}.{path}", base_key)
            return v  # None

        return walk(comp, "", None)

    # -------------------------------------------------------------- envelope --
    def convert_command(self, cmd, screen):
        """command -> $interpolate over its variable parts (§2.1/§2.2)."""
        res = cmd
        bindings = {}
        tkey = self.scen.get("target_key")
        if tkey and screen.get("target"):
            pat = re.compile(r"(?<!\S)" + re.escape(screen["target"]) + r"(?!\S)")
            if pat.search(res):
                res = pat.sub("{{" + tkey + "}}", res)
                bindings[tkey] = "scenario." + tkey
                self.ref_scen(tkey)
        for m in reversed(list(re.finditer(r'(-p(?:\s+|=)([A-Za-z_][\w.\-]*)=)("([^"]*)"|\S+)', res))):
            v = m.group(4) if m.group(4) is not None else m.group(3)
            quoted = m.group(4) is not None
            skey = next((k for k, val in self.scen.items()
                         if k != "target_key" and val == v), None)
            if skey:
                repl = m.group(1) + ('"' if quoted else "") + "{{" + skey + "}}" + \
                       ('"' if quoted else "")
                res = res[:m.start()] + repl + res[m.end():]
                bindings[skey] = "scenario." + skey
                self.ref_scen(skey)
        m = re.search(r'(-m\s+)("([^"]*)"|\S+)', res)
        if m:
            v = m.group(3) if m.group(3) is not None else m.group(2)
            quoted = m.group(3) is not None
            if self.scen.get("intent") == v:
                repl = m.group(1) + ('"' if quoted else "") + "{{intent}}" + \
                       ('"' if quoted else "")
                res = res[:m.start()] + repl + res[m.end():]
                bindings["intent"] = "scenario.intent"
                self.ref_scen("intent")
        self.stats["interpolates"] += 1
        if not bindings:
            self.stats["empty_interpolates"] += 1
        return {"$interpolate": res, "$bindings": bindings, "$example": cmd}

    def convert_affordance(self, aff, live_base):
        out = {}
        for k, v in aff.items():
            kp = f"{live_base}.{k}"
            if k == "command" and isinstance(v, str):
                interp = self.build_interpolate(v)
                if interp is None:
                    interp = {"$interpolate": v, "$bindings": {}, "$example": v}
                    self.stats["interpolates"] += 1
                    self.stats["empty_interpolates"] += 1
                out[k] = interp
            else:
                out[k] = self.convert_scalar(v, kp, k)
        return out

    def convert_envelope_section(self, kind, value):
        if kind == "trailer":
            out = {}
            for k, v in value.items():
                if k in SEMANTIC_TRAILER_KEYS:
                    out[k] = v
                else:
                    out[k] = self.convert_scalar(v, "live.trailer." + k, k)
            return out
        if kind == "affordances":
            return [self.convert_affordance(a, f"live.affordances[{i}]")
                    for i, a in enumerate(value)]
        if kind == "attention":
            out = {}
            for k, v in value.items():
                if k == "top" and isinstance(v, list):
                    out[k] = [self.convert_attention_top(t, f"live.attention.top[{i}]")
                              for i, t in enumerate(v)]
                elif k == "counts" and isinstance(v, dict):
                    out[k] = {ck: self.slot(ck, f"live.attention.counts.{ck}", cv,
                                            vtype="integer")
                              for ck, cv in v.items()}
                elif isinstance(v, list):
                    out[k] = [self.convert_element(x, f"live.attention.{k}[{i}]", k)
                              for i, x in enumerate(v)]
                else:
                    out[k] = self.convert_scalar(v, f"live.attention.{k}", k)
            return out
        return value

    def convert_attention_top(self, top, live_base):
        out = {}
        for k, v in top.items():
            if k in SEMANTIC_ATTENTION_KEYS:
                out[k] = v
                continue
            kp = f"{live_base}.{k}"
            if k == "id" and isinstance(v, str):
                name = ("ask_id" if v.startswith("ask_")
                        else "event_id" if v.startswith("evt_")
                        else "session_id" if v.startswith("ses_")
                        else "id")
                out[k] = self.slot(name, kp, v)
            elif k == "affordance" and isinstance(v, dict):
                out[k] = self.convert_affordance(v, f"{live_base}.affordance")
            else:
                out[k] = self.convert_scalar(v, kp, k)
        return out

    def convert_context(self, ctx):
        out = {}
        for k, v in ctx.items():
            if k in SEMANTIC_CONTEXT_KEYS:
                out[k] = v
            else:
                out[k] = self.convert_scalar(v, "context." + k, k)
        return out

    # ------------------------------------------------------------------ root --
    def convert(self, screen):
        self.reset()
        if screen.get("$schema") == SCHEMA_V1:
            return screen, False
        if screen.get("$schema") != SCHEMA_V2:
            raise SystemExit(f"unexpected schema {screen.get('$schema')!r}")
        self.stats["timelike"] = self.measure_timelike(screen)
        out = {"$schema": SCHEMA_V1, "id": screen["id"]}

        # scenario extraction order: tree-root, target, command (exemplar order)
        self.root_scenario_keys(screen)
        target_keys = self.target_scenario_keys(screen)
        if target_keys:
            self.scen["target_key"] = target_keys[0]
        self.command_scenario_keys(screen)

        tree_root = None
        if screen.get("archetype") == "tree":
            verb = screen["id"].split(".")[1] if "." in screen["id"] else "tree"
            tree_root = slugify(verb)

        pre = {}
        if "target" in screen and screen["target"] is not None:
            tkey = self.scen["target_key"]
            pre["target"] = self.slot(tkey, "scenario." + tkey, screen["target"])
            self.ref_scen(tkey)
        if "command" in screen:
            pre["command"] = self.convert_command(screen["command"], screen)
        if "elapsed_ms" in screen:
            pre["elapsed_ms"] = self.slot("elapsed_ms", "live.elapsed_ms",
                                          screen["elapsed_ms"], vtype="integer")
        if "context" in screen:
            pre["context"] = self.convert_context(screen["context"])
        pre["archetype"] = screen["archetype"]
        pre["component"] = self.convert_component(screen.get("component") or {},
                                                  tree_root)
        if "audit_op" in screen:
            pre["audit_op"] = self.slot("audit_op", "live.audit_op",
                                        screen["audit_op"])
        for k in ("attention", "trailer", "affordances"):
            if k in screen:
                pre[k] = self.convert_envelope_section(k, screen[k])

        # prune scenario to referenced keys, preserving extraction order (§R8)
        scen_out = {}
        for key, val in self.scen.items():
            if key != "target_key" and key in self.stats["scenario_refs"]:
                scen_out[key] = val
        if scen_out:
            out["scenario"] = scen_out

        for k, v in screen.items():
            if k in SEMANTIC_ROOT_KEYS or k in ("isolated", "isolated_reason"):
                if k == "$schema":
                    continue
                out[k] = v
                continue
            if k == "id":
                continue
            out[k] = pre.get(k, v)
        return out, True


# ------------------------------------------------------------------ file IO --
def detect_style(raw):
    compact = "\n" not in raw.rstrip("\n")
    try:
        raw.encode("ascii")
        ascii_only = True
    except UnicodeEncodeError:
        ascii_only = False
    ensure_ascii = ascii_only or ("\\u" in raw)
    trailing = raw.endswith("\n")
    return {"compact": compact, "ensure_ascii": ensure_ascii, "trailing": trailing}


def dump_screen(obj, style, sort_keys=False):
    if style["compact"]:
        text = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=style["ensure_ascii"])
    else:
        text = json.dumps(obj, indent=2, sort_keys=sort_keys,
                          ensure_ascii=style["ensure_ascii"])
    if style["trailing"]:
        text += "\n"
    return text


def convert_screen_inplace(path, conv):
    raw = open(path, encoding="utf-8").read()
    screen = json.loads(raw)
    out, changed = conv.convert(screen)
    if not changed:
        return False
    style = detect_style(raw)
    open(path, "w", encoding="utf-8").write(dump_screen(out, style))
    return True


def convert_screen_stats(path, conv):
    """Convert without writing; returns (changed, out, style, raw)."""
    raw = open(path, encoding="utf-8").read()
    out, changed = conv.convert(json.loads(raw))
    return changed, out, detect_style(raw), raw


def find_screen_files():
    out = []
    for root, _dirs, fnames in os.walk(SCREENS_DIR):
        for fn in sorted(fnames):
            if fn.endswith(".json"):
                out.append(os.path.join(root, fn))
    return sorted(out)


def screens_equal_instantiated(a_text, b_text):
    """Byte-equality after $example instantiation (acceptance 11)."""

    def inst(v):
        if isinstance(v, list):
            return [inst(x) for x in v]
        if isinstance(v, dict):
            if "$slot" in v:
                return inst(v["$example"])
            if "$interpolate" in v:
                return inst(v["$example"])
            return {k: inst(x) for k, x in v.items()}
        return v

    return json.dumps(inst(json.loads(a_text)), sort_keys=True) == \
        json.dumps(inst(json.loads(b_text)), sort_keys=True)


# --------------------------------------------------------------- embed mode --
EMBED_HEAD = re.compile(
    r"### 5\.\d+ [^\n]*\(`(screens/[^`]+)`\)[^\n]*\n"
    r"(?:[^\n]*\n)*?"
    r"```json\n")

def convert_embeds(md_path=STRUCTURE_PATH):
    md = open(md_path, encoding="utf-8").read()
    s5 = md.index("## 5. Canonical Screen Fixtures")
    s6 = md.index("## 6. Fixture Schema")
    sec = md[s5:s6]
    conv = ScreenConverter()
    report = []
    spans = []
    for m in EMBED_HEAD.finditer(sec):
        rel = m.group(1)
        bstart = m.end()
        bend = sec.index("\n```", bstart)
        spans.append((m.start(), bstart, bend, rel))
    for start, bstart, bend, rel in reversed(spans):
        screen_path = os.path.join(WIREFRAME_ROOT, rel)
        raw = open(screen_path, encoding="utf-8").read()
        screen = json.loads(raw)
        converted, changed = conv.convert(screen)
        if not changed:
            converted = screen  # already v1 — regenerate block from current file
        block = sec[bstart:bend]
        style = detect_style(block)
        style["compact"] = False
        style["trailing"] = False
        new_block = dump_screen(converted, style)
        sec = sec[:bstart] + new_block + sec[bend:]
        report.append((rel, screens_equal_instantiated(new_block, raw)))
    sec = sec.replace("Fixture (`wireframe/v2`)", "Fixture (`wireframe/v1`)")
    sec = sec.replace("Every fixture is a `wireframe/v2` root",
                      "Every fixture is a `wireframe/v1` root")
    md = md[:s5] + sec + md[s6:]
    open(md_path, "w", encoding="utf-8").write(md)
    return report, conv


# -------------------------------------------------------------- states mode --
def component_slot_keys(component):
    """Component keys (any depth) whose value holds a $slot/$interpolate object."""
    keys = set()

    def walk(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, dict) and ("$slot" in x or "$interpolate" in x):
                    keys.add(k)
                else:
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)

    walk(component)
    return keys - DIAGNOSTIC_CORE


def instantiate(text):
    def inst(v):
        if isinstance(v, list):
            return [inst(x) for x in v]
        if isinstance(v, dict):
            if "$slot" in v or "$interpolate" in v:
                return inst(v["$example"])
            return {k: inst(x) for k, x in v.items()}
        return v
    return inst(json.loads(text))


def regenerate_domain_fields():
    states_raw = open(STATES_PATH, encoding="utf-8").read()
    states = json.loads(states_raw)
    derived = {}
    for path in find_screen_files():
        screen = json.load(open(path, encoding="utf-8"))
        if screen.get("$schema") != SCHEMA_V1:
            continue
        comp = screen.get("component") or {}
        domain = comp.get("domain")
        if not domain:
            continue
        derived.setdefault(domain, set()).update(component_slot_keys(comp))
    y = states.get("6") or {}
    domains = y.get("domains") or sorted(derived)
    new_fields = {d: sorted(derived[d]) for d in domains if derived.get(d)}
    old = y.get("domain_fields")
    if old == new_fields:
        print("domain_fields: no diff (idempotent)")
        return False
    y["domain_fields"] = new_fields
    states["6"] = y
    text = json.dumps(states, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if states_raw.endswith("\n"):
        text += "\n"
    open(STATES_PATH, "w", encoding="utf-8").write(text)
    print("domain_fields regenerated (yield-state scope):")
    for d in sorted(new_fields):
        print(f"  {d}: {new_fields[d]}")
    return True


# --------------------------------------------------------------------- main --
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--files", nargs="+", help="specific screen files")
    ap.add_argument("--embeds", action="store_true", help="convert §5 embeds")
    ap.add_argument("--states", action="store_true", help="regen domain_fields")
    ap.add_argument("--check", action="store_true", help="idempotency check")
    ap.add_argument("--stats", action="store_true", help="print measured counts")
    args = ap.parse_args()

    if args.states:
        regenerate_domain_fields()
        return 0

    if args.embeds:
        report, conv = convert_embeds()
        print(f"embeds converted: {len(report)}")
        for rel, match in report:
            flag = "byte-match(post-instantiation)" if match else "MISMATCH"
            print(f"  {rel:58s} {flag}")
        if args.stats:
            print(f"slots={conv.stats['slots']} interpolates={conv.stats['interpolates']}")
        mism = [r for r, m in report if not m]
        return 1 if mism else 0

    files = args.files or find_screen_files()

    if args.check:
        drift = []
        for f in files:
            before = open(f, "rb").read()
            conv = ScreenConverter()
            out, changed = conv.convert(json.loads(before.decode("utf-8")))
            if not changed:
                continue
            after = dump_screen(out, detect_style(before.decode("utf-8"))).encode("utf-8")
            if after != before:
                drift.append(f)
        if drift:
            print(f"IDEMPOTENCY DRIFT ({len(drift)}):")
            for f in drift:
                print("  " + f)
            return 1
        print(f"idempotency check OK: {len(files)} files stable")
        return 0

    n = 0
    totals = {"slots": 0, "interpolates": 0, "empty_interpolates": 0, "timelike": 0}
    conv = ScreenConverter()
    for f in files:
        raw = open(f, encoding="utf-8").read()
        out, changed = conv.convert(json.loads(raw))
        for k in totals:
            totals[k] += conv.stats[k]
        if changed:
            open(f, "w", encoding="utf-8").write(dump_screen(out, detect_style(raw)))
            n += 1
    print(f"converted {n}/{len(files)} screens")
    if args.stats:
        # recount slot/interpolate objects over the final state
        slots = interp = empty = 0
        for f in files:
            stack = [json.load(open(f, encoding="utf-8"))]
            while stack:
                cur = stack.pop()
                if isinstance(cur, dict):
                    if "$slot" in cur:
                        slots += 1
                    if "$interpolate" in cur:
                        interp += 1
                        empty += (not cur["$bindings"])
                    stack.extend(cur.values())
                elif isinstance(cur, list):
                    stack.extend(cur)
        print(f"slot objects: {slots}")
        print(f"interpolate objects: {interp} (empty-bindings: {empty})")
        print(f"time-like component value hits (§R2 detector, pre-conversion): {totals['timelike']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
