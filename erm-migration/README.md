# ERM_RO_Dashboard: Slate to React migration

Fixes and architecture diagrams from the Slate-to-React gap analysis.

| Path | What it is | Status |
|---|---|---|
| `backend/executeAddEditWorkflow.ts` | Patched Foundry function: ARM read access is derived on the server from stored vs final board state (gap G-32). `executeAddEditWorkflow.diff` is the change against the previous version. | Deployed |
| `react-patch/erm-react-toast-and-list-refresh.patch` | React patch (11 files): app-wide toast provider, success feedback on dashboard create/edit, list refresh that waits for the saved dashboard, risk edit drawer toast fix (gaps G-33, G-34). | Not deployed |
| `react-src/src/` | The same React change as full files (11 files, same paths as the app's `src/`). Copy them over the app's files instead of applying the patch. | Not deployed |
| `diagrams/erm-legacy-full.html` | Archify architecture diagram of the legacy Slate app (shell + 7 modules). | — |
| `diagrams/erm-react-full.html` | Archify architecture diagram of the React + OSDK app. | — |

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
