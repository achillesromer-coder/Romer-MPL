# MPL Engine — Pre-release Hardening Control Record

Date: 2026-08-09
Status: PRE-RELEASE / TEST GATE
Canonical repository: `achillesromer-coder/Romer-MPL`
Canonical runtime source: `index.html`
Canonical workbook: `1uXs-uPDCN8xNFErkAOrCEeYv0ctzoZb5XUYop5UEBvE`
Controlled Drive folder: `1eRmR6kkNimF-U6-r6bQI9C7pWskc27W9`

## Purpose

This branch hardens the existing MPL Engine without introducing semantic release-version branding. It preserves the established Römer visual language while correcting runtime geometry, navigation, model-language, data-boundary and provenance defects.

## Camera / globe invariant

The globe camera is controlled by physical altitude rather than an arbitrary zoom factor:

`camera radius = 1 + altitude_km / 6371.0088`

Römer visualization limits:

- minimum camera altitude: 1 km;
- initial camera altitude: 11,500 km;
- launch-site focus altitude: 80 km;
- maximum camera altitude: 40,000 km.

The 1 km floor is a Römer UI/rendering safety constraint. It is not represented as an Australian Space Agency MPL requirement. The camera may approach but cannot cross the Earth surface.

## Method boundary

The application remains a screening/decision-support implementation of the Australian Space Agency Maximum Probable Loss Methodology published 1 August 2019. Regulatory-parity HVA inclusion requires independently derived Flight Safety Code risk-hazard-analysis geometry, including the 10^-7 probability-of-impact isopleth. The current azimuth/distance HVA weighting is explicitly identified as `ROMER_SCREENING_HEURISTIC`.

## Runtime controls

- no semantic version label in the pre-release UI;
- explicit PRE-RELEASE stage receipt;
- controlled embedded snapshot for anonymous browser reads;
- Apps Script treated as a separate operator/write transport concern;
- one `calculateMPL` implementation;
- one satellite popup implementation;
- one WebGL context-loss/restoration listener pair;
- no legacy `S.zoom` camera state;
- no ambiguous TODO/TBD/FIXME/WIP implementation markers;
- deterministic model-evidence review instead of direct external AI analysis;
- 110% analytical margin labelled `Model Buffer`, not an insurance determination;
- explicit operational empty states rather than dash placeholders.

## Browser acceptance gate

`tests/browser_globe_probe.mjs` exercises:

1. desktop and mobile boot;
2. WebGL context and active rendering;
3. panel collapse/expand and accessibility state;
4. zoom button, repeated zoom and 1 km hard floor;
5. reset-view altitude;
6. Object-view rejection without a selected site;
7. actual site selection and step navigation;
8. transit, vehicle and failure-mode selection;
9. Globe -> Object -> Orbit -> Globe transitions;
10. Advanced Parameters and Parameter Sweep;
11. Vehicle Editor, Settings, Runs and Batch surfaces;
12. Run Simulation -> object view -> simulation -> forced failure -> MPL result rendering;
13. deterministic evidence review;
14. New Mission state reset;
15. visible `undefined`/`NaN` detection.

No candidate is promoted to `main`, Drive or the workbook audit trail until the browser gate passes and the public route is reverified.