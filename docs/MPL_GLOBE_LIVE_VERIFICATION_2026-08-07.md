# MPL Globe Live Verification — 2026-08-07

## Release

- Product repair merge: `cbadbc716d229af9c68e282a5c3c0154d1afb54b`
- Browser-tested `index.html` bytes: `440088`
- Browser-tested source SHA-256: `16a3460b1b30a178db0deb5c2153eebb2d0191c06f8c63e3e229d32ad36fc6fe`
- Controlled Drive file: `11no0F0hjEHdBXTiqyzNOvuwZZDoygrmf`
- Pre-hotfix Drive backup: `1bTsouJ2aQvr8szZp1IZxNTQSq-9X-b8I`
- Canonical workbook receipts: `CL-019`, `AUD-009`

## Public surfaces verified

- `https://achillesromer-coder.github.io/Romer-MPL/`
- `https://romer.industries/mpl-engine` → embedded GitHub Pages application

Both public surfaces were fetched and executed in Chromium after the product merge.

### Desktop live receipt

- canvas: `1300 × 910`
- globe inside `.panel-wrap`: `false`
- telemetry parent: `#app`
- WebGL2: present
- context lost: `false`
- renderer calls during probe: ~`141`
- rendered triangles: ~`72,148`
- page-level runtime exceptions: `0`

### Responsive candidate receipt

- mobile viewport: `430 × 932`
- visible globe canvas: `430 × 836`
- setup panel auto-collapsed: `true`
- WebGL2: present / not lost
- zoom interaction: `1.0 → 1.2`
- page-level runtime exceptions: `0`

## Repaired faults

1. Missing `#panel` closing boundary nested `#globe-wrap` inside `.panel-wrap`, collapsing the visible globe canvas to `300 × 0` and pulling telemetry into `.main`.
2. GDP overlay function-hoisting recursion caused `Maximum call stack size exceeded`.
3. Incorrect TopoJSON distribution path caused resource/ORB failure followed by `topojson is not defined`.
4. Cloud visualisation depended on cross-origin/404 image resources.
5. Mobile presentation left the 300 px mission panel in document flow, reducing a 430 px viewport globe to only 130 px wide.

## Controls now in place

- explicit iframe-safe flex/min-height globe geometry;
- corrected DOM boundary assertions;
- deterministic GDP dispatcher;
- corrected TopoJSON client plus procedural-map fallback;
- deterministic same-document procedural cloud layer;
- WebGL context-state receipt;
- responsive overlay/auto-collapse behaviour;
- permanent Playwright/Chromium browser regression test with desktop/mobile screenshots, runtime JSON and exact tested release source archived as a workflow artifact.

The separate Google Apps Script browser-CORS limitation remains a data-transport issue. It does not affect globe rendering; the current app falls back to embedded release data. The appropriate follow-up is a same-origin or controlled snapshot transport, not weakening browser security controls.
