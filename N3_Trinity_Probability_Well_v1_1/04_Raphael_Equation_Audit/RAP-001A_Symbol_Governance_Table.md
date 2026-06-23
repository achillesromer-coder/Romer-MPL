# RAP-001A — Symbol Governance Table

Version: v1_1 governance build  
Date: 2026-06-24

## Governance rule

Each symbol has one canonical meaning within each explicitly named domain. Cross-domain reuse is prohibited unless the domain prefix is present.

| Symbol | Canonical TPW meaning | Domain | Dimensional class | Allowed contexts | Prohibited reuse / risk | Status |
|---|---|---|---|---|---|---|
| `Xi` | Sum of two fair six-sided dice for component `i` | TPW probability | Dimensionless integer | Enumeration, product probability | Continuous coordinate without declaration | LOCKED |
| `x=(x1,x2,x3)` | TPW sum-state triple | TPW probability | Dimensionless integer vector | State-space rows | Physical position vector | LOCKED |
| `k` | One-dimensional dice-sum value | TPW probability | Dimensionless integer | `k∈{2,...,12}` | Free continuous index | LOCKED |
| `n(k)` / `W(k)` | Count of ordered 2d6 outcomes producing `k` | TPW probability | Count | Weight vector, PMF | Field amplitude | LOCKED |
| `P(x)` | Joint TPW probability | TPW probability | Dimensionless probability | Product measure | Physical pressure, potential | LOCKED |
| `S` | Raw component sum `x1+x2+x3` | TPW geometry | Dimensionless scalar | Raw-sum normalization | Entropy symbol or action | LOCKED |
| `b_i` | Raw-sum barycentric coordinate `xi/S` | TPW geometry | Dimensionless coordinate | Simplex embedding | Marginal probability unless stated | LOCKED |
| `q_i` | Weight-normalized coordinate `W(xi)/ΣW(xj)` if used | TPW geometry | Dimensionless coordinate | Weight-compositional embedding | Joint probability | CONDITIONAL |
| `H(b)` | Shannon entropy of a composition | Information theory | Bits if log2 | Entropy analysis | Physical Hamiltonian | LOCKED |
| `d_B` | Barycentric distance from centroid | TPW geometry | Dimensionless | Ring metrics | Physical distance without scale | LOCKED |
| `d_E` | Euclidean distance after ternary projection | TPW geometry | Dimensionless projection distance | Projection audit | Physical distance without scale | LOCKED |
| `Ω` | Finite state space | TPW probability | Finite set | Enumeration definition | Frequency domain or cosmological density unless scoped | LOCKED |
| `Σ` | Summation operator or simplex symbol only when declared | General mathematics | Contextual | Summation/simplex notation | Stress tensor without domain prefix | CONDITIONAL |
| `Γ` | No locked TPW meaning | Reserved | N/A | Use only after definition | Path, connection, gamma function drift | RESERVED |
| `Ψ` | No locked TPW meaning | Raphael hypothesis | Pending | May denote proposed wave/state function only in hypothesis register | Proven wavefunction or TPW probability | RESERVED / UNSUPPORTED |
| `Φ` | No locked TPW meaning | Raphael hypothesis | Pending | Proposed scalar/adaptive field only after definition | Entropy, potential, probability | RESERVED / UNSUPPORTED |
| `R` | Use `r` for TPW radius; reserve `R` only after declared | Mixed | Pending | Geometry if scoped | Ricci scalar/radius drift | UNLOCKED |
| `g` | No TPW physical metric accepted | Raphael/geometry | Pending | Abstract metric only if defined | Gravity constant, tensor, tension conflation | UNLOCKED |
| `T` | No canonical TPW theorem meaning | Mixed | Pending | Tensor/trajectory only if named | Tensor/trajectory drift | UNLOCKED |
| `v` | No canonical TPW velocity meaning | Mixed | Pending | Vertex vector only if scoped | Velocity without dynamics | UNLOCKED |
| `L` | No canonical TPW action/Lagrangian | Mixed | Pending | Log-likelihood only if declared | Lagrangian/action without mechanics proof | UNLOCKED |
| `D_μ` | No TPW covariant derivative | Raphael/physics | Pending | Hypothesis only after definition | Established operator claim without audit | UNSUPPORTED |

## Required symbol hygiene

- Use `b_i` for raw-sum barycentric coordinates.
- Use `q_i` only for weight-compositional coordinates.
- Do not call `b_i` or `q_i` the joint probability.
- Use domain prefixes for Raphael-side symbols until exact equations are transcribed and audited.
