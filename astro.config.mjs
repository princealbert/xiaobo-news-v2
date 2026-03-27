// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  output: 'static',
  integrations: [react()],  // 启用 React 支持
  build: {
    format: 'directory'
  },
  vite: {
    plugins: [tailwindcss()]
  }
});
