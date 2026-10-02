# ERM_RO_Dashboard: Slate to React migration

Fixes and architecture diagrams from the Slate-to-React gap analysis.

| Path | What it is | Status |
|---|---|---|
| `backend/executeAddEditWorkflow.ts` | Patched Foundry function: ARM read access is derived on the server from stored vs final board state (gap G-32). `executeAddEditWorkflow.diff` is the change against the previous version. | Deployed |
| `react-patch/erm-react-toast-and-list-refresh.patch` | React patch (11 files): app-wide toast provider, success feedback on dashboard create/edit, list refresh that waits for the saved dashboard, risk edit drawer toast fix (gaps G-33, G-34). | Not deployed |
| `diagrams/erm-legacy-full.html` | Archify architecture diagram of the legacy Slate app (shell + 7 modules). | — |
| `diagrams/erm-react-full.html` | Archify architecture diagram of the React + OSDK app. | — |

## Applying the React patch

Paths in the patch are relative to the React app's source root (for example `pages/DashboardListPage.tsx`).

```bash
git apply --directory=src erm-migration/react-patch/erm-react-toast-and-list-refresh.patch   # if the code lives under src/
```

Add `--ignore-whitespace` if the files use Windows line endings.
