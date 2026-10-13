<!-- exception: shallow — 43 ledger rows; max honest depth 4; padding refused -->
- Template identity
  - A template (tpl://<type>/<slug>) is an ephemeral scaffolding blueprint with zero runtime presence
  - Hydration dissolves the template into a concrete routine or schema
  - Static templates are immutable and uneditable at runtime
  - Hydration runs the scaffold operation

- Addressing
  - Registry world blueprints: tpl://registry/world/<name>@<ver>
  - Registry routine blueprints: tpl://registry/routine/<name>@<ver>
  - Local micro-patterns: tpl://routine/* — webhook_receiver, idempotent_action, chunked_batch
  - Registry addresses resolve URL and SHA-256 against the local cached index.json
  - URP grammar: see: kernel.md

- Authoring operations
  - sys template new <name> --type routine|world authors a blueprint under templates/
  - sys template pack <dir> [--out bundle.cap] freezes a blueprint into an immutable SHA-256-signed bundle
  - sys template sync refreshes the local registry index.json
  - sys template import <urp|url|file> [--sha256 <hash>] imports a template
  - `capcli sys template scaffold tpl://<type>/<slug> <target> [-p k=v]` hydrates draft files into routines/ or world envs/

- Intake pipeline
  - Intake gates
    - Download staging: streams land in isolated tmpfs /scratch; streams exceeding 5MB abort immediately
    - Pack ceiling: world template bundles enforce the 5MB ceiling
    - Stream integrity: the kernel verifies SHA-256 against the index or the --sha256 flag before archive extraction; mismatch aborts with exit 3
    - Version compatibility: min_kernel_version or policy_version mismatch aborts intake with exit 3
    - Code validity: a routine template failing py_compile aborts intake with exit 3
    - Complexity gate: validation enforces AST complexity ≤10 before disk write
    - Schema gate: validation enforces schema.yaml syntax (Sub-check 1) and bundle semantics (Sub-check 2) before disk write
  - Parameter binding: -p values validate against manifest inputs at stamping
  - Source pinning: direct URL imports accept raw GitHub URLs only with #sha256=<hex>; mutable branch pulls (@main) denied
  - Exit-code contract: see: kernel.md

- Content law
  - Unpack handles declarative text and AST-analyzed code only; post-install scripts, shell hooks, and dynamic execution during unpack are banned; static AST expansion only
  - Bundle manifest: capcli-template.yaml declares typed inputs, a provides map, and min_kernel_version; bundle contract: see: artifacts/templates.yaml
  - Governance boundary: templates cannot bundle or alter policy.yaml or governance.yaml; the host governance compiler overrides all; template governance: see: artifacts/governance.yaml
  - Expansion: scaffolds expand through typed template parameters; blind regex and sed substitutions are banned

- Trust floor
  - Remote templates register at draft trust (v1) in dev
  - Imported routines, views, and verbs register at draft trust (v1) with zero promotional credit
  - Prod intake is denied; templates unpack strictly into the dev worktree; prod direct-init is denied
  - Trust ladder and promotion: see: kernel.md

- Template registry
  - A dedicated central GitHub repository serves as the PR-driven marketplace
  - Intake PRs require 100% green CI
    - CI runs validation on capcli-template.yaml
    - CI enforces shape law: tokens ≤2000 hard ceiling; complexity and params lint are advisories
    - CI executes a headless sandbox test simulation
    - CI builds a frozen .cap bundle via the sys template pack operation and computes SHA-256
  - Merged PRs trigger a release workflow
    - exception: binary — LED-0686 defines exactly two release actions; entry fields decompose below
    - The workflow publishes an immutable bundle.cap asset
    - The workflow appends an index.json entry
      - urp
      - version
      - sha256
      - bundle_url
      - min_kernel_version
      - policy_version
  - The sys template sync operation refreshes the local registry index.json

- Scaffold emissions
  - Scaffold emits exactly one audit event per hydration: routine.draft for the routine kind, env.init_from_template for the world kind
  - routine.draft carries template_source, template_hash, trust, version
  - env.init_from_template carries source_uri, bundle_sha256, schema_version, seed_tables_count
  - Environments provision empty, or populated from a world template via `capcli sys template scaffold tpl://registry/world/<name>@<ver> <target> [-p k=v]`
  - Migration-safety rehearsal executes on a temporary snapshot
  - Table seed row caps: see: kernel.md
  - Audit spine: see: kernel.md
