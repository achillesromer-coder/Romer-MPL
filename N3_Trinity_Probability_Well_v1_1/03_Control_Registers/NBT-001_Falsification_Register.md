# NBT-001 — Falsification Register

Version: v1_1 governance build  
Date: 2026-06-24

| ID | Claim | Class | Falsification condition | Required test/artifact | Status |
|---|---|---:|---|---|---|
| TPW-ENUM-001 | TPW contains exactly 1331 sum-state triples. | P0/P2 | Enumeration not equal to `11^3`. | Master enumeration CSV; validation report. | PASS |
| TPW-ENUM-002 | TPW corresponds to 46656 ordered primitive outcomes. | P0/P1 | Product primitive count not equal to `36^3`. | Validation report; algebraic derivation. | PASS |
| TPW-PROB-001 | Product probabilities sum to 1. | P1/P2 | Exhaustive probability sum differs from 1. | Validation report. | PASS |
| TPW-PROB-002 | `(7,7,7)` is the unique maximum-probability state. | P1/P2 | Any other state has probability ≥ `1/216`. | Dataset scan; maximum-state proof. | PASS |
| TPW-GEO-003 | Raw-sum simplex mapping is non-injective. | P1/P2/P3 | Every raw triple maps to a unique normalized point. | Validation report: unique normalized points < 1331. | PASS |
| RAP-ENT-001 | TPW hub equals a unique entropy optimum/modal attractor. | P5 | Formal proof fails or conflates uniform-simplex entropy with product-mode probability. | Dedicated entropy theorem. | OPEN |
| RAP-GRAV-001 | TPW is physically equivalent to a gravity well. | P4/P5 | No energy functional, field equation, or conservation law exists. | RAP-004; dimensional audit. | ANALOGY ONLY |
| RAP-SPIRAL-001 | Spiral traversal is intrinsic/necessary. | P3/P5 | Spiral only appears after imposed ordering. | Spiral invariant proof. | VISUALIZATION ONLY |
| RAP-PILOT-001 | Pilot-wave visual layer has predictive power. | P5 | Out-of-sample forecast fails benchmark. | Benchmark/test protocol. | UNVALIDATED |
| RAP-MMB-001 | MMB/non-locality framework is proven. | P5 | No formal information-theoretic or quantum-correspondence proof. | Formal theorem pack. | HYPOTHESIS |
| RAP-SCALE-001 | Scale-free isomorphism is proven. | P5 | No bijection/operator/invariant preservation proof. | Isomorphism proof file. | UNPROVEN |
| RAP-NBODY-001 | N-variable product-measure generalization is valid. | P1 | Product-measure formula does not normalize. | APP-H finite N schema. | CONDITIONAL |
| RAP-NBODY-002 | N-body physical mechanics follows from TPW. | P5 | No Hamiltonian/Lagrangian/force-law derivation. | Physics derivation and validation. | NOT PROVEN |
