# MPL Pre-release Deployment Receipt — 2026-08-10

## Status

**Deployment and provenance closure complete for the accepted PRE-RELEASE executable.**

This receipt does not declare a semantic release and does not change the MPL model or executable. It records the accepted source, validation gates, merge, controlled Drive mirror and public publication chain.

## Accepted executable identity

- Executable: `index.html`
- Size: `430297` bytes
- SHA-256: `494090da38d50c0effe033353e326184bd3a2d2f3a5d1fd632c40d3fb573d19c`
- Git blob SHA: `b4fadd9ac6854bc6a6dab93098fcab20b5b41956`
- Runtime stage: `PRE-RELEASE`
- Semantic versioning: disabled

The archived browser-tested executable and merged `main/index.html` resolve to the same Git blob SHA. The accepted artifact was also independently hashed before Drive synchronization.

## Validation acceptance

Final PR-head acceptance gates before merge:

- MPL Pre-release Validation — run `31337943351` — **SUCCESS**
- MPL Browser Regression — run `31337943344` — **SUCCESS**

The browser gate covered desktop and mobile Chromium/WebGL execution including boot, side-panel state, 1 km radial camera hard surface, Globe/Object/Orbit views, model-phase and scenario-override contracts, a rendered simulated mishap result, parameter sweep, deterministic evidence review, ACHILLES batch, run history and acknowledged write transport.

The 1 km camera floor remains a Römer rendering/collision invariant, not an Australian Space Agency regulatory requirement.

## GitHub deployment

- Repository: `achillesromer-coder/Romer-MPL`
- Pull request: `#7` — `Harden MPL Engine pre-release runtime and model controls`
- PR head accepted: `0e678c34c7cfcf4d793a285355d70bff4dfd5155`
- Squash merge commit on `main`: `4cfeafbfbdf52db5d4d946354bcdaa990deca896`
- Product executable on merged `main`: Git blob `b4fadd9ac6854bc6a6dab93098fcab20b5b41956`

## Controlled Google Drive mirror

Canonical controlled Drive object was updated **in place**, preserving its file ID:

- Canonical file ID: `11no0F0hjEHdBXTiqyzNOvuwZZDoygrmf`
- Canonical title: `romer_mpl_PRE_RELEASE.html`
- Parent folder: `1eRmR6kkNimF-U6-r6bQI9C7pWskc27W9`
- Size after update: `430297` bytes
- SHA-256 after independent re-download: `494090da38d50c0effe033353e326184bd3a2d2f3a5d1fd632c40d3fb573d19c`
- Byte comparison against accepted browser artifact: **IDENTICAL**

Pre-deployment Drive backup preserved before replacement:

- Backup ID: `1Hs-lMZo9Wg9fI645OJ7ce5EtMvAl43eu`
- Backup title: `romer_mpl_v0.2.0_PRE_PRE_RELEASE_DEPLOY_2026-08-10.html`

## Workbook provenance

Canonical workbook: `MPL Engine` — `1uXs-uPDCN8xNFErkAOrCEeYv0ctzoZb5XUYop5UEBvE`

Final closure receipts appended without rewriting historical entries:

- `CL-022` — `DEPLOYMENT_PROVENANCE`
- `AUD-011` — `DEPLOYMENT_PROVENANCE_CLOSURE`

Existing preliminary hardening receipts `CL-020`, `CL-021` and `AUD-010` remain preserved.

## Public publication chain

- GitHub Pages target: `https://achillesromer-coder.github.io/Romer-MPL/`
- Römer presentation target: `https://romer.industries/mpl-engine`

The Squarespace MPL navigation currently resolves to `/mpl-engine`. The Squarespace-to-GitHub-Pages embed relationship was previously browser-verified and the publication target was not changed in this deployment. During this closure, the search/browser cache could not independently rehydrate the direct `/mpl-engine` document; therefore this receipt does **not** invent a new post-merge rendered-browser observation. Deployment identity is instead closed by the green final-head browser acceptance plus byte-identical accepted executable on merged `main` and Drive.

## Regulatory/model boundary retained

This remains a controlled screening and decision-support artefact. It is not regulator approval or application-ready specialist evidence. Regulatory-parity HVA inclusion remains dependent on independently derived Flight Safety Code `10^-7` probability-of-impact isopleth geometry and application-grade use remains dependent on independent specialist validation.
