import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // ─── PWA: manifest + service worker (installabile da home screen) ───
    VitePWA({
      registerType: 'autoUpdate', // il SW si aggiorna da solo a ogni deploy
      includeAssets: ['logo.png', 'apple-touch-icon.png'],
      manifest: {
        name: 'CucinIAmo — Menù su misura con l\'AI',
        short_name: 'CucinIAmo',
        description:
          'Crea menù personalizzati con l\'AI per colazione, pranzo, cena o l\'intera giornata, con calorie sotto controllo.',
        lang: 'it',
        display: 'standalone',
        start_url: '/',
        theme_color: '#F7F6F9',
        background_color: '#F7F6F9',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          {
            src: 'pwa-maskable-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
        // ⚠️ Non intercettare gli URL riservati di Firebase (/__/auth/...):
        // servono al flusso di login Google (popup/redirect)
        navigateFallbackDenylist: [/^\/__\//],
        runtimeCaching: [
          // Google Fonts: CSS (può cambiare) e font (immutabili)
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'StaleWhileRevalidate',
            options: { cacheName: 'google-fonts-css' },
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-files',
              expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 365 },
            },
          },
        ],
      },
    }),
  ],
})
