# Romer-MPL ACHILLES Orchestration

This is the existing bounded orchestration marker for Romer-MPL. It does not create a second canonical task system or data master.

## Role

Romer-MPL owns Maximum Probable Loss modelling and related bounded risk/disposition analysis. It may consume receipted GMAT/mission-analysis exports and return compact machine/human outputs to LightSpeed/Cognigrex and the owning Drive/Type-1 evidence surfaces.

Achilles governs source authority, reconciliation, gates and provenance through the existing Achilles P.A / ACR3 / canonical-owner architecture. Git remains implementation and reproducible lineage.

## Rules

- Update existing models/contracts/interfaces before creating new ones.
- Prefer stable pointers and compact receipts over copying canonical datasets into the repo.
- Preserve model/source/version, assumptions, units, uncertainty and evidence classification with every decision-useful output.
- Keep GMAT propagation semantics distinct from MPL risk/loss semantics.
- Keep physical, regulatory, specialist-validation and publication gates independent from successful software/model execution.
- Archive/delete only after unique-content, canonical-destination, readback and recovery checks.
