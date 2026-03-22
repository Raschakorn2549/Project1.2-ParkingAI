import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/data':       'http://localhost:5000',
      '/send_line':  'http://localhost:5000',
      '/video_feed': 'http://localhost:5000',
    }
  }
})