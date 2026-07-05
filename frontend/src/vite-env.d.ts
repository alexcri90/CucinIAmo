/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** URL del backend API (senza protocollo, es: christmas-menu-api.onrender.com) */
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
