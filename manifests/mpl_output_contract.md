# Romer-MPL Output and Interoperability Contract

## Purpose

Romer-MPL converts governed analysis inputs into compact, decision-ready Maximum Probable Loss and related risk outputs without duplicating the canonical source corpus.

## Functional boundary

**MPL means Maximum Probable Loss.**

Romer-MPL may consume validated GMAT/mission-planning exports and may return compact outputs to LightSpeed, Römer workspaces, calculators/simulators, Data/Operations views and future Cognigrex surfaces. These interfaces do not collapse the underlying methodologies or authority boundaries.

- GMAT owns its propagation/model output semantics for the identified run/configuration.
- Romer-MPL owns its controlled risk/loss calculation semantics.
- LightSpeed/Cognigrex owns execution/routing/workspace integration.
- Drive/Type-1/project canon owns reviewed input/evidence authority.

No output should imply launch-permit approval, regulator acceptance, mission feasibility, physical-system validation or independent specialist sign-off unless the separate evidence gate exists.

## Required input receipt

Before an external model output is consumed, bind at minimum:

- source/model identity and version;
- scenario/run identity;
- input dataset/source pointers;
- units and coordinate/frame semantics where applicable;
- epoch/time basis;
- configuration/assumption set;
- generation timestamp and reproducibility pointer;
- evidence/maturity classification.

## Preferred output types

- risk ranges and loss envelopes;
- disposition and sensitivity summaries;
- route/mission burden summaries where methodologically supported;
- launch-window or event summaries sourced from the identified mission-analysis receipt, not re-derived by MPL without authority;
- recommended next configurations for review;
- compact Sheets/workbook rows;
- machine-readable receipts for LightSpeed/Cognigrex;
- public-safe summaries only after publication/claim gates.

## Output flow

```text
Owning canonical inputs
  -> GMAT / other governed model when required
  -> receipted model export
  -> Romer-MPL calculation
  -> compact result + assumptions + provenance + uncertainty
  -> LightSpeed / Cognigrex workspace and routing
  -> owning Type-1 / Data / Operations evidence surfaces
  -> publication only after independent gates
```

## Avoid

- copying the full canonical corpus into this repository;
- raw result overload where a receipted compact representation is sufficient;
- silent unit/frame/epoch conversion;
- conflating GMAT dynamics with MPL methodology;
- treating a screen, heuristic, visual layer or model run as regulator-approved evidence;
- public display of unreviewed assumptions or sensitive internal state.
