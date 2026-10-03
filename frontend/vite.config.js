import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    // HMR shares the HTTP port Vite actually bound. Do not set hmr.port —
    // that opened a second listener (ERR_SERVER_ALREADY_LISTEN). Open the
    // URL Vite prints (3000, or the next free port if 3000 is taken).
    strictPort: false,
    hmr: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true
      }
    }
  }
})