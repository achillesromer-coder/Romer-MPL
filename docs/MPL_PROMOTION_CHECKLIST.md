# MPL Engine — Promotion Checklist

A pre-release candidate may be promoted only when every required control below has an inspectable receipt.

- [ ] `index.html` JavaScript syntax passes.
- [ ] No duplicate DOM IDs.
- [ ] Exactly one `calculateMPL` implementation.
- [ ] Exactly one satellite popup implementation.
- [ ] Exactly one WebGL context-loss/restoration listener pair.
- [ ] No legacy `S.zoom`, direct public Sheet-read helper or direct external AI-analysis transport.
- [ ] Camera reaches but cannot cross the 1 km Römer visualization floor.
- [ ] Reset returns to 11,500 km camera altitude.
- [ ] Side panel collapse/expand preserves a non-zero globe viewport.
- [ ] Object view rejects a missing site instead of silently displaying an empty surface.
- [ ] Site -> transit -> vehicle -> failure-mode workflow binds state correctly.
- [ ] Globe -> Object -> Orbit -> Globe transition is renderable.
- [ ] Advanced Parameters and Parameter Sweep produce finite rendered results.
- [ ] Vehicle Editor, Settings, Runs and Batch surfaces open and close.
- [ ] Run Simulation enters the object simulation view.
- [ ] Failure event produces a finite MPL result and visible result surface.
- [ ] Deterministic evidence review renders without an external AI provider call.
- [ ] New Mission returns explicit operational states rather than dash placeholders.
- [ ] Desktop browser acceptance passes.
- [ ] Mobile browser acceptance passes.
- [ ] No visible `undefined` or `NaN` state is detected.
- [ ] Static audit has no blocking high/critical finding.
- [ ] Public GitHub Pages deployment is browser-verified after merge.
- [ ] Squarespace `/mpl-engine` embed resolves to the verified candidate.
- [ ] Exact tested HTML is synchronized to controlled Drive.
- [ ] Canonical workbook Changelog and Audit_Trail receipts are appended and re-read.

Unchecked items are not placeholders for product behaviour; they are release controls and remain outside the runtime implementation.