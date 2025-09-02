import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

// Build directly into FastAPI's static directory with stable filenames
export default defineConfig({
  plugins: [react()],
  root: ".",
  build: {
    outDir: "app/static",
    emptyOutDir: false, // don't nuke other static assets
    assetsDir: "assets",
    rollupOptions: {
      input: "webui/main.tsx",
      output: {
        entryFileNames: "assets/[name].js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
})
