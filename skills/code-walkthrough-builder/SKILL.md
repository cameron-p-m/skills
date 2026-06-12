---
name: code-walkthrough-builder
description: Build interactive, static HTML walkthroughs that explain a code path one file or important logic block at a time. Use when the user asks for a code walkthrough, trace diagram, interactive explainer, architecture flow, or file-by-file guided tour with clickable source links.
---

# Code Walkthrough Builder

Create a polished standalone HTML walkthrough for understanding a code flow. The output should feel like an interactive technical document, not a dashboard.

## Workflow

1. **Trace the flow first**
   - Use `rg` to find entrypoints, handlers, helpers, tests, and downstream enforcement.
   - For PR or branch tours, identify the real base ref and inspect `git diff <base> -- <file>`; do not substitute latest-code snippets for changed hunks.
   - Read enough code to identify the real sequence and side effects.
   - Choose one step per file or important logic block. Avoid tiny implementation-only steps.

2. **Define step data**
   - For each step, capture: title, file path, line range, phase, timing/mode, summary, "what to notice", "why it matters", and code content.
   - For PR or branch tours, code content must be a real unified diff hunk from the base ref. Select the hunk that intersects the line range; if no hunk intersects, use the nearest changed hunk from the same file and make that choice explicit in the step summary.
   - Use latest-code excerpts only for non-diff walkthroughs where there is no meaningful base ref.
   - Use the first line in the line range for editor deep links.
   - Keep diff hunks short enough to scan; prefer the decision point over surrounding boilerplate.

3. **Build one static HTML file**
   - Do not require a dev server unless the user explicitly asks.
   - Use semantic HTML, inline CSS copied from `assets/walkthrough-style.css`, and a small inline script.
   - Include: left rail with filterable steps, previous/next controls, keyboard left/right navigation, a step header, a full-width code/diff card, and explanation panels.
   - Make the active step diff-led: render step metadata/title/summary first, the code card immediately after, then "what to notice" and "why it matters" panels underneath.
   - Do not include a horizontal top step strip when there are many steps; it will crowd and wrap poorly.

4. **Editor links**
   - Add Cursor links for every step:
     `cursor://file<absolute-path>:<line>:1`
   - Encode path segments with `encodeURIComponent`, preserving `/`.
   - Keep the visible label specific, e.g. `Open in Cursor at line 881`.

## Visual Style

Copy `assets/walkthrough-style.css` into the generated HTML's `<style>` block as the baseline. Then adjust only the title-specific hero copy, optional ASCII sketch, and any user-requested visual tweaks.

- Calm reader palette: soft off-white/blue page background, white cards, light gray-blue borders.
- Diff-first reading: the code card should be the widest and most visually important surface in the active step.
- For PR tours, render real diff lines with `@@`, `+`, and `-` markers, and visually distinguish added, removed, and hunk-header rows.
- Use a dark code panel, but avoid pure-black page chrome and heavy black borders.
- Prefer sans-serif prose for descriptions and monospace only for code, file paths, badges, and compact technical labels.
- Keep headings readable rather than oversized; avoid all-lowercase styling unless the project specifically asks for it.
- Rounded cards and pill controls are fine; avoid drop shadows and loud dashboard styling.
- Optional hero ASCII/box-drawing sketch when it clarifies the flow, but keep it visually secondary.

## HTML Pattern

Use a data-driven script:

- `const steps = [...]`
- `renderList()` for the left navigation.
- `renderStep()` for the active step header, full-width code/diff card, and explanation panels.
- `renderDiff()` or equivalent for PR tours; it should render hunk headers, added lines, removed lines, and context lines from an item `diff` field.
- `setActiveStep(index)` clamps the index and rerenders.
- `applyFilter()` filters by title, file, phase, and summary.
- Keyboard handler ignores the search input and uses `ArrowLeft` / `ArrowRight`.

Recommended active-step DOM order:

1. Badges, step counter, title, and summary.
2. `.code-card` with file label, Cursor link, and excerpt.
3. `.detail-grid` containing "what to notice" and "why it matters".
4. Previous/next controls and keyboard hint.

## Validation

Before finishing:

- Run the repo formatter/linter for the generated file when available.
- Execute the inline script syntax with `new Function(script)`.
- For PR or branch tours, assert every step has a real diff hunk with at least one added or removed line.
- Use `jsdom` when available to assert:
  - expected number of step buttons render,
  - initial step is correct,
  - next/previous or keyboard navigation works,
  - filtering finds a known step,
  - Cursor links include the expected absolute path and line.
- If browser automation cannot inspect a `file://` URL, say so and rely on local DOM validation.

## Guardrails

- Do not invent source paths or line numbers; derive them from local files.
- Do not add marketing copy or feature explanations outside the walkthrough itself.
- Keep the file self-contained unless the user asks for a packaged app.
- Preserve unrelated working-tree changes.
