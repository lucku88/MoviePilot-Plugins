import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const pluginRoot = path.resolve(__dirname, '..')
const distRoot = path.join(pluginRoot, 'dist', 'assets')
const nestedAssetsRoot = path.join(distRoot, 'assets')

fs.mkdirSync(nestedAssetsRoot, { recursive: true })

const copyPairs = [
  [path.join(distRoot, 'style.css'), path.join(nestedAssetsRoot, 'style.css')],
  [path.join(distRoot, 'remoteEntry.js'), path.join(nestedAssetsRoot, 'remoteEntry.js')],
]

for (const [src, dest] of copyPairs) {
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest)
  }
}

const chunkNames = fs.existsSync(distRoot)
  ? fs.readdirSync(distRoot)
  : []

const replacements = [
  ['${__federation_expose_./Page}', chunkNames.find((name) => /^__federation_expose_Page-.*\.js$/.test(name))],
  ['${__federation_expose_./Config}', chunkNames.find((name) => /^__federation_expose_Config-.*\.js$/.test(name))],
]

function patchRemoteEntry(remoteEntryPath) {
  if (!fs.existsSync(remoteEntryPath)) return

  let content = fs.readFileSync(remoteEntryPath, 'utf8')

  for (const [token, chunkName] of replacements) {
    if (!chunkName || !content.includes(token)) continue

    const chunkPath = path.join(distRoot, chunkName)
    let relativeImport = path.relative(path.dirname(remoteEntryPath), chunkPath).replace(/\\/g, '/')
    if (!relativeImport.startsWith('.')) {
      relativeImport = `./${relativeImport}`
    }
    content = content.split(token).join(relativeImport)
  }

  fs.writeFileSync(remoteEntryPath, content)
}

patchRemoteEntry(path.join(distRoot, 'remoteEntry.js'))
patchRemoteEntry(path.join(nestedAssetsRoot, 'remoteEntry.js'))
