# Römer MPL route/source systematic audit — 2026-07-21

Status: `CONTROLLED_INTERNAL / RELEASE_GATE_BLOCKED`

## Authority and scope

- Live route declared by owner: `https://romer.industries/mpl`.
- Git authority: `achillesromer-coder/Romer-MPL`.
- Operational source file: `index.html`.
- Source blob observed during audit: `34741b3cf8923cb55fe7c6ccaabdb3f5f1ba2053`.
- Source lineage: commit `27bf2d90278c9f36d3fad941daf8a0433ac51f07`, which renamed `romer_mpl_v0.00.1 (1).html` to `index.html`.
- The application remains a single-file HTML/CSS/JavaScript platform.
- This audit does not alter `index.html`, the live route, Sheets, Apps Script, ACHILLES, Drive, webhooks or deployment state.

The route is publicly linked by the Römer Industries site, but the audit environment could not independently retrieve and render `/mpl`. Live visual identity and browser interaction therefore remain pending Codex/Playwright evidence.

## Regulatory source reconciliation

The controlling public methodology found is the Australian Space Agency **Maximum Probable Loss Methodology**, published 1 August 2019. The Agency states that its own estimator is not comprehensive, is not a substitute for independent specialist advice, and cannot be used in an application.

Current legal context also includes:

- `Space (Launches and Returns) Act 2018`, current compilation dated 14 October 2024.
- `Space (Launches and Returns) (Insurance) Rules 2019`, in force.
- `Space (Launches and Returns) (General) Rules 2019`, current compilation dated 4 February 2025.

Primary sources:

- https://www.space.gov.au/about-agency/publications/maximum-probable-loss-methodology
- https://www.legislation.gov.au/C2004A00391/latest
- https://www.legislation.gov.au/F2019L01120/
- https://www.legislation.gov.au/F2019L01118/latest

## Initial source findings

| ID | Severity | State | Finding | Release effect |
|---|---:|---|---|---|
| MPL-REG-001 | Critical | Fail | The same build labels its basis as `ASA 2019`, `ASA METHODOLOGY: 2019`, and `ASA MPL CONSTANTS — AUD 2024`. | Method/version provenance is not singular or reproducible. |
| MPL-CLAIM-001 | Critical | Review required | Metadata and result surfaces use unqualified `ASA-compliant` or `ASA MPL — PASS` wording. | A model check can be mistaken for regulator acceptance. |
| MPL-CLAIM-002 | Critical | Fail | The IIP probability badge is hard-coded to `< 1×10⁻⁷`. | The UI can display an uncalculated safety threshold as demonstrated. |
| MPL-MODEL-001 | High | Review required | The visualization estimates downrange as `altitude × 2.8` before great-circle projection. | Screening IIP may be mistaken for an application-grade trajectory product. |
| MPL-MODEL-002 | High | Review required | HVA weighting uses a custom inverse-distance/Gaussian azimuth corridor heuristic while citing ASA sections. | Custom analytical policy is not clearly separated from published methodology. |
| MPL-BUG-001 | High | Fail | Risk points store `risk`, while color selection reads `latest.zone`. | Heat-map category/color can fall through incorrectly. |
| MPL-BUG-002 | High | Fail | At five seconds or less before failure, the FSS status expression returns `NOMINAL`. | The display can understate imminent failure. |
| MPL-SEC-001 | High | Fail | Webhook dispatch uses `no-cors` and then reports a verified-success toast. | Delivery cannot actually be confirmed from the opaque response. |
| MPL-SEC-002 | High | Review required | Imported configuration may set any URL beginning with `http` as a webhook destination. | Mission, operator and risk data can leave the system without a strong destination trust gate. |
| MPL-SEC-003 | High | Review required | Multiple dynamic surfaces use template interpolation with `innerHTML`. | Sheet-derived, imported or custom text needs escaping/injection tests. |
| MPL-CLAIM-003 | High | Review required | Browser-generated reports are marked `RESTRICTED — REGULATORY USE ONLY`. | Users may infer application suitability from fallback or unverified data. |
| MPL-PROV-001 | High | Open | Regulatory/economic constants are embedded in the source rather than a versioned source registry. | Individual values lack machine-readable authority, section, units and review status. |
| MPL-PROV-002 | Medium | Open | Run/report packets do not carry an immutable Git/model hash or complete data snapshot receipt. | Exact reproduction of a result is not established. |
| MPL-DATA-001 | High | Open | Sites, vehicle casualty areas, explosive yields, fragments, failure multipliers, population zones and HVAs have embedded fallback values. | Each value requires source/evidence status and a fallback-data indicator. |
| MPL-LIVE-001 | High | Blocked | Live `/mpl` rendered behavior was not independently retrieved in this audit environment. | Source-to-deployment identity, responsive layout and network behavior require browser evidence. |

## Existing positive controls

- The source contains `<meta name="robots" content="noindex">`.
- Locked integration identifiers are declared for the MPL Sheet, ACHILLES workbook, Drive folder and Apps Script deployment.
- The repository preserves the earlier orchestration PR #1 as a draft and has not merged it.
- No source deletion or live-route change was made by this audit.
- The initial audit harness has 12 dependency-free unit tests; local result: **12/12 passed**.

## Systematic lanes 1–7

### Lane 1 — source and data authority

1. Confirm the deployed `/mpl` artifact matches `Romer-MPL/index.html`.
2. Capture the exact Git commit/blob and all live data snapshot IDs.
3. Build a value-level registry for every constant, site, vehicle, zone, failure mode and HVA.
4. Mark each value `SOURCE_BACKED`, `SHEET_LIVE`, `FALLBACK`, `PROPOSED`, `SYNTHETIC`, `SUPERSEDED` or `REJECTED`.

### Lane 2 — epistemic separation

Separate:

- regulatory methodology;
- legal/insurance requirements;
- custom Römer screening heuristics;
- visualization-only flight approximations;
- measured/approved trajectory and population inputs;
- synthetic/demo fallback data;
- regulator determination.

### Lane 3 — equations, units and falsification

For every MPL component, record equation, input units, source section, uncertainty, domain and falsification test. The custom HVA corridor weighting and IIP projection must not be attributed to ASA without exact source support.

### Lane 4 — dual verification

- Smith: static, unit, browser and integration tests.
- Oracle: independent methodology, reasoning, trust-boundary and claim-language review.
- Achilles: release and evidence gate.
- A model may enter controlled review after mathematical and independent reasoning passes.
- Regulatory/application language remains blocked without specialist and owner approval.

### Lane 5 — Neo return packet

Neo must return:

- source commit/blob;
- data snapshot IDs;
- model/method versions;
- inputs and units;
- outputs and uncertainties;
- test receipts;
- failed and rejected records;
- exact destination and deployment receipt.

### Lane 6 — held fields

Collaborators, customer/operator commitments, licensing conclusions and Mission 1 values remain held. No regulatory approval, insurer acceptance or application readiness may be inferred.

### Lane 7 — consolidation and release control

- Keep the existing live route unchanged.
- Preserve PR #1 and all historical source.
- Reconcile Codex automation outputs against this branch before any overlapping edit.
- Do not merge, deploy or remove `noindex` until all critical/high failures have receipts.
- Archive before any disposal; no deletion is proposed by this audit.

## Required soft-launch gates

1. **Source identity:** browser-deployed file hash/commit matches approved Git source.
2. **Regulatory wording:** replace regulator-compliance claims with model-state wording unless independently approved.
3. **Method registry:** one methodology version with exact citations and value-level provenance.
4. **Probability integrity:** no threshold displayed unless calculated and evidenced.
5. **Model separation:** screening IIP/HVA heuristics are visibly separate from application-grade analysis.
6. **Security:** imported config schema, HTTPS destination control, explicit outbound-data confirmation, safe DOM construction.
7. **Receipts:** verifiable Sheets/ACHILLES/Drive/webhook acknowledgements; `ATTEMPTED` is not `DELIVERED`.
8. **Regression:** static audit, unit tests, browser matrix, offline/fallback tests, outbound-write mocks and accessibility checks pass.
9. **Data state:** live versus fallback data is visible in UI and report.
10. **Run provenance:** report includes commit/blob, model version, data snapshots, method version and evidence state.

## Current disposition

`RELEASE_GATE_BLOCKED`.

The current route may remain available as a controlled, noindex, internal/demo surface. It should not be represented as an application-ready regulator calculator or as evidence of regulator approval. Final LS soft launch and broader Cognigrex systematic operation remain deferred to the owner's next prompt.
