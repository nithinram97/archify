import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
const r = (p: string) => path.resolve(__dirname, p);
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: [
    { find: '@fca0-enterprise-risk-management/sdk', replacement: r('mock/sdk.ts') },
    { find: '@osdk/client', replacement: r('mock/client.ts') },
    { find: '@osdk/oauth', replacement: r('mock/oauth.ts') },
    { find: '@osdk/foundry.admin', replacement: r('mock/admin.ts') },
    { find: '@tinymce/tinymce-react', replacement: r('mock/tinymce.tsx') },
    { find: /^@\//, replacement: r('@') + '/' },
  ] },
});
