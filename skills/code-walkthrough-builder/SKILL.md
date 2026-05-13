---
name: code-walkthrough-builder
description: Build interactive, static HTML walkthroughs that explain a code path one file or important logic block at a time. Use when the user asks for a code walkthrough, trace diagram, interactive explainer, architecture flow, or file-by-file guided tour with clickable source links.
---

# Code Walkthrough Builder

Create a polished standalone HTML walkthrough for understanding a code flow. The output should feel like an interactive technical document, not a dashboard.

## Workflow

1. **Trace the flow first**
   - Use `rg` to find entrypoints, handlers, helpers, tests, and downstream enforcement.
   - Read enough code to identify the real sequence and side effects.
   - Choose one step per file or important logic block. Avoid tiny implementation-only steps.

2. **Define step data**
   - For each step, capture: title, file path, line range, phase, timing/mode, summary, "what to notice", "why it matters", and a short code excerpt.
   - Use the first line in the line range for editor deep links.
   - Keep excerpts short enough to scan; prefer the decision point over surrounding boilerplate.

3. **Build one static HTML file**
   - Do not require a dev server unless the user explicitly asks.
   - Use semantic HTML, inline CSS copied from `assets/walkthrough-style.css`, and a small inline script.
   - Include: left rail with filterable steps, previous/next controls, keyboard left/right navigation, a main explanation panel, and a code card.
   - Do not include a horizontal top step strip when there are many steps; it will crowd and wrap poorly.

4. **Editor links**
   - Add Cursor links for every step:
     `cursor://file<absolute-path>:<line>:1`
   - Encode path segments with `encodeURIComponent`, preserving `/`.
   - Keep the visible label specific, e.g. `Open in Cursor at line 881`.

## Visual Style

Copy `assets/walkthrough-style.css` into the generated HTML's `<style>` block as the baseline. Then adjust only the title-specific hero copy, optional ASCII sketch, and any user-requested visual tweaks.

- White page background and white panels.
- Monospace type throughout.
- Strong black borders.
- Rounded corners on large boxes, tighter corners on buttons and inputs.
- No drop shadows or offset shadows.
- Lowercase, text-forward headings.
- Compact technical labels and badges.
- Optional hero ASCII/box-drawing sketch when it clarifies the flow.

## HTML Pattern

Use a data-driven script:

- `const steps = [...]`
- `renderList()` for the left navigation.
- `renderStep()` for the active detail/code card.
- `setActiveStep(index)` clamps the index and rerenders.
- `applyFilter()` filters by title, file, phase, and summary.
- Keyboard handler ignores the search input and uses `ArrowLeft` / `ArrowRight`.

## Validation

Before finishing:

- Run the repo formatter/linter for the generated file when available.
- Execute the inline script syntax with `new Function(script)`.
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
