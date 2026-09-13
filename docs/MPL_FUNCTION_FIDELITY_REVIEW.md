# Römer MPL — Function, Fidelity and Interface Review

**State:** PRE-RELEASE  
**Purpose:** bounded review contract for functional completeness, interface fidelity, visual usability and evidence boundaries. This document does not confer regulatory, empirical, specialist or public-release authority.

## Review doctrine

A feature is not promoted because it is visible, labelled HIGH, or passes CI. For each surface distinguish:

- **implemented** — source/runtime behavior exists;
- **source-gated** — static contract is machine checked;
- **browser-gated** — desktop/mobile browser behavior has a source-bound receipt;
- **evidence-gated** — model result carries source/method/provenance sufficient for its intended use;
- **external-gated** — independent specialist, regulator, provider, empirical or other external evidence is still required.

Persistent boundaries:

- `REFERENCE PRESET != VALIDATED RESULT`
- `CI/TEST PASS != EMPIRICAL VALIDATION`
- `UI FIDELITY != SCIENTIFIC FIDELITY`
- `BROWSER GMAT SCENARIO != GMAT EXECUTION`
- `PRE-RELEASE != PUBLICLY RELEASED`

## Function review matrix

| Surface | Current function | Review state | Required evidence before promotion |
| --- | --- | --- | --- |
| Boot / controlled snapshot | Loads embedded controlled workbook snapshot without cross-origin Sheet dependency | IMPLEMENTED / SOURCE+HISTORICAL-BROWSER-GATED | fresh current-source browser/provider receipt |
| Mission setup | Guarded site → mission → advanced configuration flow | IMPLEMENTED / BROWSER-GATED HISTORICALLY | fresh current-source browser receipt after material source changes |
| Globe navigation | Globe/Object/Orbit views with explicit no-data states | IMPLEMENTED / BROWSER-GATED HISTORICALLY | current-source browser receipt |
| Surface zoom | Hard Earth radial surface and 1 km rendering floor | IMPLEMENTED / SOURCE+NEAR-SURFACE-GATED HISTORICALLY | current-source browser/LOD receipt if executable changes |
| Responsive panel | Desktop/mobile collapse and expansion with ARIA state | IMPLEMENTED / BROWSER-GATED HISTORICALLY | current-source desktop+mobile receipt |
| Failure scenario | Selectable failure path and run-result calculation | IMPLEMENTED / MODEL-RUNTIME-GATED | genuine source-bound run receipt for GST-063 vertical slice |
| Phase / override logic | Model phase rules and scenario overrides | IMPLEMENTED / MODEL-RUNTIME+HISTORICAL-BROWSER-GATED | current-source receipt on model changes |
| Parameter sweep | Controlled scenario/sensitivity sweep | IMPLEMENTED / BROWSER-GATED HISTORICALLY | receipt tied to any decision-useful exported result |
| Evidence review | Methodology/evidence review without external AI permit prediction | IMPLEMENTED | provenance + evidence-state binding per exported result |
| ACHILLES batch | Bounded candidate/run handoff | IMPLEMENTED / INTERFACE-GATED | durable run receipt + compact Operations pointer |
| Mission history | Run-history surface | IMPLEMENTED | distinguish demonstration/reference rows from operational receipts |
| Operator write transport | Acknowledged Apps Script POST path | IMPLEMENTED / TRANSPORT-GATED HISTORICALLY | current acknowledgement/provider receipt for release promotion |
| PDF/data export | Export controls present | IMPLEMENTED | output hash + source/run binding for decision-useful artifacts |
| GMAT interoperability | Optional governed import/export boundary | CONTRACTED | genuine GMAT execution receipt; browser scenario is insufficient |
| Regulatory HVA parity | 10^-7 hazard geometry dependency | EXTERNAL-EVIDENCE-GATED | independently derived controlled Flight Safety Code geometry |
| Application-grade MPL | Specialist validation dependency | EXTERNAL-EVIDENCE-GATED | qualified independent specialist validation |

## Fidelity review

### Interface fidelity

The interface must keep PRE-RELEASE state visible, preserve source/evidence boundaries, expose unavailable/degraded states rather than fabricate data, and retain explicit distinction between reference examples and validated/operational results.

### Scientific fidelity

Runtime detail settings such as `PHYSICS_FIDELITY=HIGH` describe selected internal calculation/rendering detail only. They do not establish empirical validity, regulator acceptance, independent specialist validation or scientific truth.

### Spatial fidelity

Near-surface imagery is contextual rendering and is not hazard geometry. The 1 km camera floor is a rendering/collision control, not a regulator requirement. External imagery outages must fall back to the controlled global surface without changing MPL calculations.

### Operational fidelity

A GST-063 vertical slice is closed only when one real source-bound run produces a durable receipt, compact Operations pointer, `/wN/data` evidence expansion and provider/browser readback. A demonstration row or historical browser pass cannot substitute for that chain.

## Aesthetic / usability review

The live MPL workbook uses the same functional information architecture while improving scanability:

- Contents: stronger title/purpose/block/header hierarchy; wrapped descriptions; frozen navigation columns/rows; wider descriptive fields.
- Mission Log: persistent identifiers frozen during horizontal review; high-contrast wrapped headers; top-aligned operational rows.
- MPL→ACHILLES bridge: persistent bridge/run identifiers frozen; consistent title/header hierarchy; no model-value mutation.

The browser surface should continue to favour functional clarity over ornamental density. Refinements should prioritise state visibility, input grouping, responsive control reachability, keyboard/focus semantics, reduced-motion support, receipt visibility and degraded-state messaging before adding visual effects.

## Automated review

`tests/ui_fidelity_static_audit.py` produces a machine-readable source/UI receipt with hard contracts and non-blocking advisories. `.github/workflows/mpl-pre-release-validation.yml` runs and archives that receipt alongside source, runtime and systematic-audit evidence.

A passing static audit is necessary but not sufficient for current browser/provider promotion.

## Current GST-063 closure sequence

1. Keep Romer-MPL source/config authority bound to the canonical MPL Engine workbook.
2. Run the current executable through a genuine supported runtime path.
3. Persist the source-bound durable run receipt.
4. Write/read back only the compact receipt/pointer into existing Type 1 Operations authority.
5. Project evidence to the existing W4/W5 + `/wN/data` surfaces.
6. Obtain desktop/mobile/provider readback.
7. Independent audit.
8. Master finalisation.
9. Release-state promotion only after exact provider proof.
