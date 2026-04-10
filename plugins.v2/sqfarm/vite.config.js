import fs from 'node:fs'
import path from 'node:path'

import federation from '@originjs/vite-plugin-federation'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

function sqfarmAssetIsolation() {
  return {
    name: 'sqfarm-asset-isolation',
    closeBundle() {
      const distDir = path.resolve(__dirname, 'dist/assets')
      const originalCss = path.join(distDir, 'style.css')
      const isolatedCssName = 'sqfarm-style.css'
      const isolatedCss = path.join(distDir, isolatedCssName)

      if (!fs.existsSync(originalCss)) {
        return
      }

      if (fs.existsSync(isolatedCss)) {
        fs.rmSync(isolatedCss, { force: true })
      }
      fs.renameSync(originalCss, isolatedCss)

      const patchTargets = []
      const queue = [distDir]
      while (queue.length) {
        const current = queue.shift()
        for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
          const fullPath = path.join(current, entry.name)
          if (entry.isDirectory()) {
            queue.push(fullPath)
            continue
          }
          if (/\.(js|html)$/i.test(entry.name)) {
            patchTargets.push(fullPath)
          }
        }
      }

      for (const filePath of patchTargets) {
        const content = fs.readFileSync(filePath, 'utf-8')
        if (!content.includes('style.css')) {
          continue
        }
        fs.writeFileSync(filePath, content.replaceAll('style.css', isolatedCssName), 'utf-8')
      }
    },
  }
}

export default defineConfig({
  plugins: [
    vue(),
    sqfarmAssetIsolation(),
    federation({
      name: 'SQFarm',
      filename: 'remoteEntry.js',
      exposes: {
        './Page': './src/components/Page.vue',
        './Config': './src/components/Config.vue',
      },
      shared: {
        vue: { requiredVersion: false, generate: false },
        vuetify: { requiredVersion: false, generate: false, singleton: true },
        'vuetify/styles': { requiredVersion: false, generate: false, singleton: true },
      },
      format: 'esm',
    }),
  ],
  build: {
    outDir: 'dist/assets',
    emptyOutDir: true,
    target: 'esnext',
    minify: false,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash][extname]',
      },
    },
  },
  css: {
    postcss: {
      plugins: [
        {
          postcssPlugin: 'internal:charset-removal',
          AtRule: {
            charset: (atRule) => {
              if (atRule.name === 'charset') {
                atRule.remove()
              }
            },
          },
        },
        {
          postcssPlugin: 'vuetify-filter',
          Root(root) {
            root.walkRules((rule) => {
              if (rule.selector && (rule.selector.includes('.v-') || rule.selector.includes('.mdi-'))) {
                rule.remove()
              }
            })
          },
        },
      ],
    },
  },
  server: {
    port: 5120,
    cors: true,
    origin: 'http://localhost:5120',
  },
})
