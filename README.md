# Römer MPL Engine

Römer Industries' pre-release Maximum Probable Loss screening and mission-risk visualisation engine. `index.html` is the executable Git source used by GitHub Pages and embedded by the Römer Industries MPL Engine page.

## Execution authority

The repository is the executable source of truth. The canonical operational data source is the Google Sheet **MPL Engine** (`1uXs-uPDCN8xNFErkAOrCEeYv0ctzoZb5XUYop5UEBvE`). Public GitHub Pages execution consumes a controlled workbook snapshot embedded in `index.html`; it does not depend on a cross-origin Sheet read during boot. Operator writes use the configured Apps Script acknowledgement path and are separate from public read/boot availability.

The current runtime is intentionally identified as **PRE-RELEASE**. Semantic release numbering is not used until a controlled release is explicitly declared.

## Model boundary

The calculation layer implements screening logic derived from the Australian Space Agency Maximum Probable Loss methodology published 1 August 2019. Outputs are decision-support artefacts, not regulator approval, permit evidence or an application-ready specialist determination.

Regulatory HVA inclusion depends on independently derived Flight Safety Code risk-hazard geometry, including the `10^-7` probability-of-impact isopleth. The application's current ±45° HVA exposure cone is identified in code and receipts as `ROMER_SCREENING_HEURISTIC`; it is not represented as that regulatory isopleth.

The composite model currency is AUD. Workbook HVA/GDP values sourced in USD are normalised through the explicit receipted screening FX rule in the snapshot. The 110% model buffer is a Römer planning sensitivity, not a regulatory or insurance requirement.

## Globe and navigation invariants

Earth uses a hard radial surface. Camera altitude is measured from the mean Earth radius (`6371 km`) and cannot fall below **1 km**. The one-kilometre floor is a Römer rendering/collision control, not an Australian Space Agency requirement. Surface overlays are constrained below that floor; atmospheric/cloud shells are hidden in near-surface operation so zoom cannot place the camera inside a visual shell.

The mission side panel is a three-step guarded state machine: site selection, mission configuration, advanced parameters. Object view requires a selected site. Orbit view explicitly renders a no-data state before trajectory data exists. Desktop and mobile panel collapse/expand state is covered by browser regression tests.

## Canonical data contracts

Runtime tables are `MPL_Config`, `MPL_Constants`, `Vehicles`, `Launch_Sites`, `High_Value_Assets`, `GDP_Table`, `Population_Zones`, `Failure_Modes`, `Operators` and `BRIDGE_W5_Targets`. Mission writes target `Mission_Log`, `Asset_Exposures` and the controlled ACHILLES bridge tables through acknowledged transport.

Vehicle `IspVac_s` and `ReferenceThrust_kN` values in the workbook are explicitly marked `PRE_RELEASE_VISUAL_MODEL`. They drive the visual kinematics only and are excluded from MPL and regulatory evidence. Operator short codes, run prefixes and display colours are also canonical workbook fields rather than hidden JavaScript seed values.

## Validation

`.github/workflows/mpl-pre-release-validation.yml` gates JavaScript syntax, source-contract invariants, model/runtime regression and the legacy systematic detector suite. `.github/workflows/mpl-browser-regression.yml` runs Chromium/WebGL desktop and mobile acceptance across boot, side navigation, panel state, 1 km zoom floor, Globe/Object/Orbit views, MPL phase rules, scenario overrides, a real simulated mishap path, parameter sweep, evidence review, ACHILLES batch, run history, vehicle editor, settings and acknowledged write transport.

Browser receipts include the exact tested `index.html`, SHA-256, JSON diagnostics and screenshots.

## Repository boundary

`N3_Trinity_Probability_Well_v1_1/` and related N³/Raphael material are preserved as separate analytical material and are not part of the MPL browser runtime. Changes in that subtree require their own provenance and validation lane rather than being silently coupled to MPL execution.

## External closure conditions

The model can operate as a controlled screening artefact with its embedded workbook snapshot. Regulatory-parity HVA treatment remains dependent on independently supplied Flight Safety Code risk-hazard geometry. Application-grade use remains dependent on independent specialist validation. Live CelesTrak station telemetry is optional visual enrichment only; failure to retrieve it must leave the MPL model unchanged and produce an explicit unavailable state rather than fabricated orbital data.

Machine-readable current state is recorded in `docs/MPL_PRE_RELEASE_STATE.json`.
