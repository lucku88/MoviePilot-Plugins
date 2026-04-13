const scriptRel = 'modulepreload';const assetsURL = function(dep) { return "/"+dep };const seen$1 = {};const __vitePreload = function preload(baseModule, deps, importerUrl) {
    // @ts-expect-error true will be replaced with boolean later
    if (!true || !deps || deps.length === 0) {
        return baseModule();
    }
    const links = document.getElementsByTagName('link');
    return Promise.all(deps.map((dep) => {
        // @ts-expect-error assetsURL is declared before preload.toString()
        dep = assetsURL(dep);
        if (dep in seen$1)
            return;
        seen$1[dep] = true;
        const isCss = dep.endsWith('.css');
        const cssSelector = isCss ? '[rel="stylesheet"]' : '';
        const isBaseRelative = !!importerUrl;
        // check if the file is already preloaded by SSR markup
        if (isBaseRelative) {
            // When isBaseRelative is true then we have `importerUrl` and `dep` is
            // already converted to an absolute URL by the `assetsURL` function
            for (let i = links.length - 1; i >= 0; i--) {
                const link = links[i];
                // The `links[i].href` is an absolute URL thanks to browser doing the work
                // for us. See https://html.spec.whatwg.org/multipage/common-dom-interfaces.html#reflecting-content-attributes-in-idl-attributes:idl-domstring-5
                if (link.href === dep && (!isCss || link.rel === 'stylesheet')) {
                    return;
                }
            }
        }
        else if (document.querySelector(`link[href="${dep}"]${cssSelector}`)) {
            return;
        }
        const link = document.createElement('link');
        link.rel = isCss ? 'stylesheet' : scriptRel;
        if (!isCss) {
            link.as = 'script';
            link.crossOrigin = '';
        }
        link.href = dep;
        document.head.appendChild(link);
        if (isCss) {
            return new Promise((res, rej) => {
                link.addEventListener('load', res);
                link.addEventListener('error', () => rej(new Error(`Unable to preload CSS for ${dep}`)));
            });
        }
    }))
        .then(() => baseModule())
        .catch((err) => {
        const e = new Event('vite:preloadError', { cancelable: true });
        // @ts-expect-error custom payload
        e.payload = err;
        window.dispatchEvent(e);
        if (!e.defaultPrevented) {
            throw err;
        }
    });
};

const exportSet = new Set(['Module', '__esModule', 'default', '_export_sfc']);
      let moduleMap = {
"./Page":()=>{
      dynamicLoadingCss(["style.css"]);
      return __federation_import('./../__federation_expose_Page-ebd14eb9.js').then(module =>Object.keys(module).every(item => exportSet.has(item)) ? () => module.default : () => module)},
"./Config":()=>{
      dynamicLoadingCss(["style.css"]);
      return __federation_import('./../__federation_expose_Config-6d06d292.js').then(module =>Object.keys(module).every(item => exportSet.has(item)) ? () => module.default : () => module)},};
    const seen = {};
    const dynamicLoadingCss = (cssFilePaths) => {
      const metaUrl = import.meta.url;
      if (typeof metaUrl == 'undefined') {
        console.warn('The remote style takes effect only when the build.target option in the vite.config.ts file is higher than that of "es2020".');
        return
      }
      const curUrl = metaUrl.substring(0, metaUrl.lastIndexOf('remoteEntry.js'));

      cssFilePaths.forEach(cssFilePath => {
        const href = curUrl + cssFilePath;
        if (href in seen) return
        seen[href] = true;
        const element = document.head.appendChild(document.createElement('link'));
        element.href = href;
        element.rel = 'stylesheet';
      });
    };
    async function __federation_import(name) {
        return __vitePreload(() => import(name),true?[]:void 0);
    }    const get =(module) => {
      if(!moduleMap[module]) throw new Error('Can not find remote module ' + module)
      return moduleMap[module]();
    };
    const init =(shareScope) => {
      globalThis.__federation_shared__= globalThis.__federation_shared__|| {};
      Object.entries(shareScope).forEach(([key, value]) => {
        const versionKey = Object.keys(value)[0];
        const versionValue = Object.values(value)[0];
        const scope = versionValue.scope || 'default';
        globalThis.__federation_shared__[scope] = globalThis.__federation_shared__[scope] || {};
        const shared= globalThis.__federation_shared__[scope];
        (shared[key] = shared[key]||{})[versionKey] = versionValue;
      });
    };

export { dynamicLoadingCss, get, init };
