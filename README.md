# Römer MPL Engine

Controlled pre-release maximum probable loss screening and decision-support engine for Australian space-activity planning.

## Canonical surfaces

- Runtime source: `index.html`
- Public route: `https://romer.industries/mpl-engine`
- Embedded application: `https://achillesromer-coder.github.io/Romer-MPL/`
- Canonical workbook: Google Sheet `1uXs-uPDCN8xNFErkAOrCEeYv0ctzoZb5XUYop5UEBvE`
- Controlled Drive folder: `1eRmR6kkNimF-U6-r6bQI9C7pWskc27W9`

## Regulatory and model boundary

The engine implements screening logic informed by the Australian Space Agency Maximum Probable Loss Methodology published 1 August 2019. It is not represented as regulator approval, an application-ready calculation or a substitute for independent specialist advice.

Regulatory-parity high-value-asset inclusion requires independently derived Flight Safety Code risk-hazard-analysis geometry, including the 10^-7 probability-of-impact isopleth. The current azimuth/distance asset weighting is therefore machine-labelled `ROMER_SCREENING_HEURISTIC`.

## Runtime architecture

The browser application is a controlled single-file runtime with Three.js visualisation and a deterministic calculation engine. Anonymous public reads use the embedded controlled snapshot. Apps Script remains a separate operator/write transport concern.

The globe camera uses physical altitude rather than an arbitrary zoom scalar. Earth radius is 6371.0088 km and the Römer rendering floor is 1 km above the model surface. The 1 km floor is a rendering invariant, not an Agency methodology requirement.

## Pre-release quality gates

Before promotion to `main` or Drive, the candidate must pass:

- JavaScript syntax and DOM-ID validation;
- static model/provenance audit;
- calculation regression tests;
- Chromium/WebGL desktop and mobile boot;
- panel/navigation geometry;
- camera-floor and reset behaviour;
- site/transit/vehicle/failure-mode workflow;
- Globe, Object and Orbit views;
- parameter sweep and batch execution;
- simulation/failure/MPL-result path;
- deterministic evidence review;
- explicit reset/empty-state validation;
- visible `undefined`/`NaN` detection.

See `docs/MPL_PRE_RELEASE_HARDENING_2026-08-09.md` for the current control record and `docs/MPL_GLOBE_LIVE_VERIFICATION_2026-08-07.md` for the last verified production receipt.

## Repository boundary

The MPL runtime and its directly supporting tests/workflows are the active execution lane. Historical or adjacent N3/Raphael research subtrees are preserved and are not silently treated as executable MPL authority.