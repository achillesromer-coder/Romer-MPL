# MPL Engine — Human / Machine Index

This index is the concise navigation surface for people and agents working on the pre-release MPL Engine.

## Human-readable authority

1. `README.md` — what the artefact is, where its canonical surfaces live and which gates control promotion.
2. `docs/MPL_PRE_RELEASE_HARDENING_2026-08-09.md` — current hardening scope and acceptance gate.
3. `docs/MPL_METHOD_BOUNDARY_2026-08-09.md` — regulatory/model/visualization boundary.
4. `docs/MPL_GLOBE_LIVE_VERIFICATION_2026-08-07.md` — last verified production browser receipt.
5. `docs/MPL_SYSTEMATIC_AUDIT_2026-07-21.md` — historical audit receipt; preserve as dated evidence rather than current work state.

## Machine-readable authority

1. `docs/MPL_CURRENT_STATE.json` — current canonical IDs, method state, camera invariants and required gates.
2. `docs/MPL_OPEN_THREADS.json` — only current unresolved engineering/evidence threads and their objective closure criteria.
3. Runtime `MODEL_META` and `CONSTANT_RECEIPTS` in `index.html` — model/data receipt shown with generated output.
4. Browser artifacts from `MPL Pre-release Browser Acceptance` — screenshots, runtime JSON and exact candidate SHA.

## Execution lane

`index.html`, `tests/`, `tools/`, `.github/workflows/` and the MPL control documents above form the active MPL execution lane.

Adjacent N3/Raphael research material is preserved but is not automatically authoritative for MPL runtime behaviour. Any future integration must explicitly identify source, transformation and acceptance evidence.

## Promotion rule

A candidate is not canonical merely because it exists on a branch. Promotion requires source gates, calculation tests and browser acceptance to pass, followed by merge, public-route verification, exact Drive synchronization and canonical workbook Changelog/Audit_Trail receipts.