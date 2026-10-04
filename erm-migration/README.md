# ERM_RO_Dashboard: Slate to React migration

Fixes and architecture diagrams from the Slate-to-React gap analysis.

| Path | What it is | Status |
|---|---|---|
| `backend/executeAddEditWorkflow.ts` | Patched Foundry function: ARM read access is derived on the server from stored vs final board state (gap G-32). `executeAddEditWorkflow.diff` is the change against the previous version. | Deployed |
| `react-patch/erm-react-toast-and-list-refresh.patch` | React patch (11 files): app-wide toast provider, success feedback on dashboard create/edit, list refresh that waits for the saved dashboard, risk edit drawer toast fix (gaps G-33, G-34). | Not deployed |
| `react-src/src/` | The same React change as full files (11 files, same paths as the app's `src/`). The toast provider is mounted in `App.tsx`; `main.tsx` needs no change. Copy them over the app's files instead of applying the patch. | Not deployed |
| `diagrams/erm-slate-detailed.html` | Detailed Archify architecture of the Slate app: shell internals, 7 modules, Foundry functions, object sets, actions and objects. | — |
| `diagrams/erm-slate-dashboard-lifecycle.html` | Archify lifecycle of a dashboard in the Slate app: statuses, versions and iterations, and who can trigger each change. | — |
| `diagrams/erm-react-detailed.html` | Detailed Archify architecture of the React app: pages, dialogs, dashboard view and tabs, OSDK client, Foundry functions, actions and objects. | — |
| `diagrams/erm-react-dashboard-lifecycle.html` | Archify lifecycle of a dashboard in the React app: statuses, locking, versions and iterations, and who can trigger each change. | — |
| `diagrams/erm-risk-lifecycle.html` | Archify lifecycle of a risk or opportunity across both apps: ARM source, per-board record, assessment, key messages, sharing, locking, carry-forward and removal. | — |
| `diagrams/erm-react-risk-lifecycle.html` | Archify lifecycle of a risk or opportunity in the React app only: Full Search and executeAddEditWorkflow, drawer and one-pager edits, key-message save and validation, sharing inbox, locking, carry-forward and removal. | — |
| `diagrams/erm-legacy-full.html` | Archify architecture diagram of the legacy Slate app (shell + 7 modules). | — |
| `diagrams/erm-react-full.html` | Archify architecture diagram of the React + OSDK app. | — |
| `docs/AI-Assisted-Legacy-App-Migration-Playbook.pdf` | The AI-assisted migration playbook: context packing with pack-project.ts, the seven steps, deliverables, teamwork, transferability and a jury demo script. | — |
| `docs/ERM-Migration-Jury-Pitch.pdf` | PDF of the ten-slide PowerPoint pitch. Animations appear as still frames. | — |
| `docs/ERM-Migration-Jury-Pitch-v2.pptx`, `docs/ERM-Migration-Jury-Pitch-v2.pdf` | Recommended eight-slide pitch in the Airbus theme, built on SCQA and Problem → Insight → Proof → Scale, each slide tagged with the award criterion it answers. Animated GIFs and auto-playing slide builds; the PDF shows still frames. | — |
| `docs/ERM-Migration-Jury-Pitch.pptx` | Ten-slide jury pitch in the Airbus theme, with speaker notes: what ERM is, adoption, why migrate, the AI method, KPIs, effort saved, business testimonials, 2026 objectives and reuse. Animated GIFs and auto-playing slide builds play in Slide Show. | — |
| `docs/gifs/legacy-breakdown.gif`, `docs/gifs/migration-to-react.gif` | The two pitch animations as standalone GIFs, in the Airbus palette. | — |

## Applying the React patch

Two copies of the same patch, differing only in line endings. Paths are relative to the React app's `src/` folder.

```bash
# Windows checkout (files use CRLF line endings)
git apply --directory=src erm-migration/react-patch/erm-react-toast-and-list-refresh.crlf.patch

# LF checkout
git apply --directory=src erm-migration/react-patch/erm-react-toast-and-list-refresh.patch
```

The "trailing whitespace" warnings on the CRLF copy are the carriage returns and are harmless. If your files have changed since the analysed code, add `--reject` to apply what matches and leave `.rej` files for the rest.

## Copying the full files instead

`react-src/src/` mirrors the app's `src/` folder. Copy it over the app's `src/` (for example `Copy-Item -Recurse -Force erm-migration\react-src\src\* src\` in PowerShell).

These files were built from the code shared on 2 Oct 2026. If any of them changed in your branch since, copying overwrites those changes: compare with `git diff` before committing.
