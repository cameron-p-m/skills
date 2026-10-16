---
name: typescript-antislop
description: Runs dmmulroy/anti-slop with a cached local Oxlint installation on changed TypeScript files, PR files, or explicit files, then guides safe fixes. Use when asked to apply anti-slop or review TypeScript against its rules; manual inspection is the fallback when execution is unavailable.
---

# TypeScript anti-slop

Run the actual [anti-slop](https://github.com/dmmulroy/anti-slop) rules before interpreting or fixing findings. The bundled runner installs pinned tooling in a personal cache, without changing the target repository's dependencies, lint configuration, or CI. Anti-slop is an opinionated policy, not a complete correctness or security check.

## Run

Read the target repository's instructions. Determine whether the request is a review or authorizes fixes. Use Python 3.10+, Git, npm, and a Node.js version that can load TypeScript source (Node 24.19+ is a suitable baseline). The first nonempty run needs network access to GitHub and npm; later runs reuse the installation. Respect sandbox and repository installation policies. Do not bypass a denied installation.

Replace `<skill>` with this skill's absolute directory and `<repo>` with the target repository root:

```sh
# Staged and unstaged tracked changes, plus untracked nonignored files.
python3 <skill>/scripts/run.py changed --repo <repo>

# Committed changes from the merge base of the actual PR base and HEAD.
python3 <skill>/scripts/run.py pr --repo <repo> --base origin/main

# Specific files, with paths relative to the repository root.
python3 <skill>/scripts/run.py files --repo <repo> -- 'src/user.ts' 'src/file with spaces.tsx'
```

- Resolve the actual PR base from PR metadata or established branch context. Do not assume `main` for a stacked PR. Ensure the local base ref is current; fetch that ref if needed and authorized. The runner does not fetch target repository refs, check out a PR, or change branches.
- The runner selects existing `.ts`, `.tsx`, `.mts`, and `.cts` files, removes duplicates, and excludes deleted paths. It preserves spaces and newlines in Git paths. An empty selection exits without installing or invoking Oxlint. Explicit directories are rejected.
- PR mode selects committed paths but lints their **current working-tree contents**. If selected files have local edits, disclose that difference. For exact PR-head results, use a clean checkout at the PR head under repository worktree instructions. PR mode excludes files changed only locally; use `changed` separately if those are in scope.
- Oxlint checks entire selected files, not only changed lines. Existing violations in those files can appear. Identify whether a finding was introduced by the change before attributing it to the PR.
- The default cache is `~/.cache/typescript-antislop/<source-revision>-<oxlint-version>`. Override it with `--cache <directory>` for an ephemeral or sandbox-writable location. That directory is tool-owned; do not point it at a project or a shared directory containing unrelated files. `setup` installs the runtime without selecting files. Do not run simultaneous first-time setups against the same cache.
- Add `--effect` only for files that use Effect. Split mixed file selections if necessary; do not apply Effect policy to unrelated TypeScript.
- The dedicated config enables all 18 general rules plus `oxc/no-accumulating-spread`. It disables the default correctness category and nested config loading to keep this a separate policy check. Git ignore behavior still applies. Inspect generated/vendor paths before running and use explicit files to narrow scope. Do not use `--no-ignore` to force a broad scan.
- If the repository has established anti-slop overrides, inspect and preserve them. Use its configured Oxlint invocation with the same explicit file selection, or adapt a copy of the cache config for that run. Do not present the standalone defaults as the repository's configured policy. Do not change repository settings merely to make this check pass.

## Interpret and fix

Read [references/rules.md](references/rules.md) for rule exceptions and rewrite hazards. Read [references/effect.md](references/effect.md) only for Effect code.

1. Inspect each diagnostic and the affected declarations and callers. A policy violation is not automatically a runtime defect. Follow repository requirements where they conflict with upstream policy and report the conflict.
2. In review mode, report findings without editing. When fixes are authorized, prefer deletion, inference, existing domain types, and existing boundary parsers. Avoid unrelated migrations and new frameworks.
3. Preserve public contracts, error behavior, side effects, and validation. In particular, preserve omitted properties, callback execution order, accumulator ownership, and method receivers. Never replace a cast with `any`, an unsupported assertion, or a false `SAFETY` comment.
4. The runner performs no automatic fixes. If applying Oxlint fixes separately, inspect the diff and use ordinary `--fix` only within the authorized scope; do not enable suggestion or dangerous fixes by default.
5. Run the repository formatter, relevant typecheck, and focused behavioral tests. Rerun the same anti-slop selection after changes. A passing lint run does not establish type correctness or behavioral equivalence.
6. Report file selection/base, applied rules, findings or changes, validation results, and unresolved conflicts. The runner returns Oxlint's failure status; do not suppress it or describe a failed run as clean.

## Manual fallback

If tooling cannot run because of network, runtime, or installation constraints, state the blocker and apply the bundled rule references by source inspection. Check all applicable rules, aliases, multiline expressions, and callers. Searches can locate candidates but cannot establish compliance. Report this as manual review, never as an Oxlint pass. Do not silently substitute manual review for a failed lint run.

## Provenance

The runner and references target upstream commit `13909c9e07590f5a85d93c62712259fe14a883f7`, with both `oxlint` and `@oxlint/plugins` pinned to `1.78.0`, matching that revision. Upstream source and its licenses are fetched into the cache; the documentation license is also included as [LICENSE](LICENSE).

Upstream uses AST and lexical-scope analysis, not the TypeScript type checker. It resolves local aliases but generally not imported contracts. Manual observations can go beyond its detection but must be labeled accordingly. To upgrade, update the source revision and both package versions together, compare exported rules and tests with the references, and rerun representative valid/invalid files and file-selection checks before using the new version.
