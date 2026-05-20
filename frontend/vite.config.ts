import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'LEON · SOPHIA',
        short_name: 'LEON·SOPHIA',
        start_url: '/',
        display: 'standalone',
        background_color: '#f6f8fa',
        theme_color: '#0969da',
        icons: [{ src: '/icon-512.svg', sizes: '512x512', type: 'image/svg+xml' }]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: []
      }
    })
  ],
  server: {
    port: 5175,
    proxy: {
      '/api': process.env.VITE_API_TARGET || 'http://localhost:8000'
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts']
  }
})
