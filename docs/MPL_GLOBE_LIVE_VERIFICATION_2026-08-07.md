# MPL Globe Live Verification — 2026-08-07

Target release merge: `cbadbc716d229af9c68e282a5c3c0154d1afb54b`

Verify both public surfaces after GitHub Pages deployment:

- `https://achillesromer-coder.github.io/Romer-MPL/`
- `https://romer.industries/mpl-engine`

Required front-facing state:

- non-zero globe canvas;
- globe is not nested in `.panel-wrap`;
- telemetry is outside `.main`;
- WebGL2 context exists and is not lost;
- renderer is actively drawing;
- no TopoJSON/GDP stack-overflow page exceptions;
- responsive candidate remains valid.
