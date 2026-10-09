# Root Justfile — Developer Inner Loop

default: check

# Fast inner-loop verification (< 15 seconds)
check:
    cargo fmt --all --check
    cargo clippy --workspace --all-targets -- -D warnings
    python3 tools/check-trinity.py
    cd packages/pwa && bun run build
    cargo test --workspace --lib

# Gate 3: Lockfile and AST schema validation
validate:
    cargo run -p capcli-cli -- rule validate
    git diff --exit-code capcli.lock artifacts/

# Trinity pointer link and token budget check
check-trinity:
    python3 tools/check-trinity.py

# Astro documentation verification
check-docs:
    cd docs && bun install --frozen-lockfile && bun run build

# SDK polyglot test suites
test-sdks:
    cd packages/ts && bun test
    cd packages/py && pytest tests/

# Tier 1 Linux Sandbox check (Linux host only)
test-sandbox:
    cargo test -p capcli-core --test test_bwrap

# Mandatory pre-push composite target (< 45 seconds)
pre-push: check validate check-docs test-sdks
