# GMAT Interoperability

This directory is the bounded interface surface between GMAT mission/orbital analysis and the existing Romer-MPL toolchain. It is not a second mission master and does not make MPL a trajectory propagator.

## Authority boundary

- **GMAT** supplies governed trajectory/state-vector, event, timing and scenario exports where those outputs are required by an MPL/risk case.
- **Romer-MPL** owns Maximum Probable Loss screening, risk/loss-envelope analysis and compact decision outputs within its controlled methodology boundary.
- **LightSpeed / Cognigrex** provides the execution, routing, workspace and canonical-interface layer for validated inputs/outputs.
- Owning Drive/Type-1 workbooks remain canonical for reviewed programme data, evidence and source authority.

A GMAT result is not regulatory MPL evidence by itself. An MPL result is not a replacement for trajectory dynamics, mission feasibility, specialist hazard geometry or regulator acceptance.

## Interface classes

Use existing files and source references first. Where durable machine interfaces are required, keep them bounded to:

- `scripts/` — governed GMAT helpers/adapters;
- `templates/` — controlled scenario templates;
- `exports/` — receipted GMAT outputs consumed by an identified MPL case.

Every imported export should carry source identity, units, epoch/time basis, coordinate/frame semantics, scenario/configuration identity and provenance sufficient to reproduce the downstream calculation. Do not silently copy large canonical datasets into this directory when a stable pointer/interface is sufficient.

## Intended flow

`canonical mission inputs -> GMAT scenario/run -> receipted GMAT export -> Romer-MPL bounded risk calculation -> LightSpeed/Cognigrex workspace/output -> owning evidence/publication gate`
