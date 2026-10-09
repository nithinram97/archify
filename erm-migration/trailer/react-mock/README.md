# ERM React app with fake data (for trailer screenshots)

Runs the real ERM React code in a browser with invented sample data, so screenshots can be taken without
Foundry, real risks or real people. Used to produce `../textures/react_*.png`.

What is replaced
- `mock/sdk.ts`: the private Foundry SDK (only API names)
- `mock/client.ts`, `mock/oauth.ts`, `mock/admin.ts`: OSDK client, sign-in and current user
- `mock/fakeData.ts`: sample dashboards, risks, mitigations and users (all invented)
- `mock/tinymce.tsx`: the rich-text editor
- `src/assets/`: neutral placeholder logos
- `@/`: the standard shadcn UI components the app imports

The app's own `src/` is not in this folder. Copy it in from the ERM repository first.

Run
```bash
cp -r <erm-react-repo>/src/* src/        # keeps src/assets placeholders if the repo has none
npm install
npx vite --port 5174 --host 127.0.0.1    # then open http://127.0.0.1:5174/dashboards
npm i -D playwright && mkdir -p out && node scripts/capture.mjs   # screenshots into out/
```
`scripts/capture.mjs <step>` runs one step (search, share2, slide2, filters, layout, report, locked, tablesave, ...).
Note: the app needs `@tanstack/react-table` 9.x (already in package.json).
