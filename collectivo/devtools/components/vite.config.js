import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from "@originjs/vite-plugin-federation";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'remote-app',
      filename: 'remoteEntry.js',
      // Modules to expose
      exposes: {
        './test_extension_modules': './src/App.vue',
        './HelloSingle2': './src/components/Hello.vue',
      },
      shared: ['vue']
    }),
  ],
  build: {
    target: ["chrome89", "edge89", "firefox89", "safari15"],
    minify: true,
  }
})
