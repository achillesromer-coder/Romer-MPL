# MPL Live Deployment Receipt — 2026-08-05

## Target

- Public route: `https://romer.industries/mpl-engine`
- Resolved embedded application: `https://achillesromer-coder.github.io/Romer-MPL/`

## Verified release identity

- Version marker: `v0.2.0`
- Served bytes: `434989`
- Served SHA-256: `630f82d48691b308ad64e90fab8ce0af57faf7368d8d9c89675cd09bdc4397fd`
- Controlled Drive file ID: `11no0F0hjEHdBXTiqyzNOvuwZZDoygrmf`
- Main source blob: `1f5646bc701d9b275c8768ff78a440b7b8fb8ab5`

## Route receipt

- Squarespace route status: `200`
- Squarespace response bytes: `116019`
- Squarespace response SHA-256: `2b77ddd29a64d8c9d777a1b8db7b20f5047a6efa49bf0b86664834da1706ba4b`
- Embedded application status: `200`
- Exact release SHA match: `TRUE`
- v0.2.0 marker detected: `TRUE`

## Release gates

- Drive payload checksum and byte size: passed
- Inline JavaScript syntax: passed
- DOM and canonical-definition gates: passed
- Detector regression suite: 12/12 passed
- Calculation runtime smoke: passed
- Canonical live-tab data contract: passed for all 10 runtime tabs
- Static release audit: `REVIEW`, `0 findings`, no blockers
- Live deployment identity: passed

The public Squarespace route and its embedded GitHub Pages application were independently fetched by GitHub Actions on 5 August 2026. The embedded application was byte-for-byte identical to the controlled Drive release.