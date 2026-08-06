import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const outDir = process.env.PROBE_OUT || 'artifacts/browser-globe';
fs.mkdirSync(outDir, { recursive: true });

const targets = [
  { name: 'github-pages', url: 'https://achillesromer-coder.github.io/Romer-MPL/' },
  { name: 'squarespace', url: 'https://romer.industries/mpl-engine' },
];

const browser = await chromium.launch({
  headless: true,
  args: [
    '--enable-webgl',
    '--ignore-gpu-blocklist',
    '--use-angle=swiftshader',
    '--enable-unsafe-swiftshader',
    '--disable-dev-shm-usage',
  ],
});

const summary = [];
let hardFailure = false;

for (const target of targets) {
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const consoleEvents = [];
  const pageErrors = [];
  const requestFailures = [];
  const responses = [];

  page.on('console', msg => consoleEvents.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', err => pageErrors.push({ message: err.message, stack: err.stack || '' }));
  page.on('requestfailed', req => requestFailures.push({ url: req.url(), failure: req.failure()?.errorText || 'unknown' }));
  page.on('response', res => {
    if (res.status() >= 400) responses.push({ url: res.url(), status: res.status() });
  });

  let navError = null;
  try {
    await page.goto(target.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(14000);
  } catch (err) {
    navError = String(err?.stack || err);
  }

  await page.screenshot({ path: path.join(outDir, `${target.name}.png`), fullPage: true }).catch(() => {});

  const frames = page.frames().map(f => ({ name: f.name(), url: f.url() }));
  let appFrame = page.mainFrame();
  if (target.name === 'squarespace') {
    appFrame = page.frames().find(f => /achillesromer-coder\.github\.io\/Romer-MPL/.test(f.url())) || appFrame;
  }

  const diag = await appFrame.evaluate(() => {
    const byId = id => document.getElementById(id);
    const canvas = byId('globe-canvas');
    const wrap = canvas?.parentElement;
    const canvasRect = canvas?.getBoundingClientRect?.();
    const wrapRect = wrap?.getBoundingClientRect?.();
    const css = canvas ? getComputedStyle(canvas) : null;
    const splash = byId('splash');
    const app = byId('app');
    let rendererState = {};
    let sceneState = {};
    let globals = {};
    let contextState = {};
    try {
      globals = {
        THREE: typeof THREE,
        threeRevision: typeof THREE !== 'undefined' ? THREE.REVISION : null,
        renderer: typeof renderer,
        scene: typeof scene,
        camera: typeof camera,
        globe: typeof globe,
      };
      if (typeof renderer !== 'undefined' && renderer) {
        rendererState = {
          width: renderer.domElement?.width || null,
          height: renderer.domElement?.height || null,
          calls: renderer.info?.render?.calls ?? null,
          triangles: renderer.info?.render?.triangles ?? null,
          memoryGeometries: renderer.info?.memory?.geometries ?? null,
          memoryTextures: renderer.info?.memory?.textures ?? null,
          outputEncoding: renderer.outputEncoding ?? null,
          toneMapping: renderer.toneMapping ?? null,
        };
      }
      if (typeof scene !== 'undefined' && scene) {
        sceneState = { children: scene.children?.length ?? null };
      }
      const gl = canvas?.getContext?.('webgl2') || canvas?.getContext?.('webgl');
      if (gl) {
        const dbg = gl.getExtension('WEBGL_debug_renderer_info');
        contextState = {
          exists: true,
          lost: gl.isContextLost(),
          version: gl.getParameter(gl.VERSION),
          shading: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
          vendor: dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
          renderer: dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
        };
      } else contextState = { exists: false };
    } catch (err) {
      rendererState.probeError = String(err?.stack || err);
    }
    return {
      href: location.href,
      title: document.title,
      readyState: document.readyState,
      versionText: document.querySelector('.tb-version')?.textContent || null,
      splash: splash ? { className: splash.className, display: getComputedStyle(splash).display, opacity: getComputedStyle(splash).opacity } : null,
      app: app ? { className: app.className, opacity: getComputedStyle(app).opacity } : null,
      canvas: canvas ? {
        present: true,
        widthAttr: canvas.width,
        heightAttr: canvas.height,
        rect: canvasRect ? { x: canvasRect.x, y: canvasRect.y, width: canvasRect.width, height: canvasRect.height } : null,
        css: css ? { width: css.width, height: css.height, display: css.display, visibility: css.visibility, opacity: css.opacity } : null,
      } : { present: false },
      wrap: wrapRect ? { width: wrapRect.width, height: wrapRect.height } : null,
      globals,
      rendererState,
      sceneState,
      contextState,
      scriptSrcs: [...document.scripts].map(s => s.src).filter(Boolean),
      bodyTextLead: document.body?.innerText?.slice(0, 800) || '',
    };
  }).catch(err => ({ probeError: String(err?.stack || err), href: appFrame.url() }));

  const record = {
    target,
    navError,
    frames,
    diagnostic: diag,
    pageErrors,
    requestFailures,
    badResponses: responses,
    console: consoleEvents,
  };
  fs.writeFileSync(path.join(outDir, `${target.name}.json`), JSON.stringify(record, null, 2));
  summary.push(record);

  if (target.name === 'github-pages') {
    const d = diag || {};
    const globeFailure = Boolean(navError) || Boolean(d.probeError) ||
      !d.canvas?.present || !(d.canvas?.rect?.width > 100 && d.canvas?.rect?.height > 100) ||
      d.globals?.THREE !== 'object' || d.globals?.renderer !== 'object' || d.globals?.scene !== 'object' ||
      d.contextState?.exists !== true || d.contextState?.lost === true ||
      !(d.rendererState?.calls > 0) || !(d.sceneState?.children > 0) ||
      pageErrors.length > 0;
    hardFailure ||= globeFailure;
  }
  await context.close();
}

fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
await browser.close();
if (hardFailure) process.exit(2);
