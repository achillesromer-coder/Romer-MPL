# RAP-002 — Dimensional Audit

Version: v1_1 governance build  
Date: 2026-06-24

## Audit rule

TPW base variables are dimensionless. Any physical interpretation must introduce units explicitly and cannot inherit proof status from TPW mathematics.

| Item | Equation / Symbol | Dimensional class | Audit result | Notes |
|---|---|---|---|---|
| `Xi` | Dice-sum variable | Dimensionless integer | PASS | finite discrete variable |
| `W(k)` | Count function | Count | PASS | integer multiplicity |
| `P(X_i=k)` | Single PMF | Dimensionless probability | PASS | denominator 36 |
| `P(x)` | Joint PMF | Dimensionless probability | PASS | denominator `36^3` |
| `S` | Raw coordinate sum | Dimensionless scalar | PASS | not entropy/action |
| `b_i` | Raw barycentric coordinate | Dimensionless ratio | PASS | sums to 1 |
| `q_i` | Weight-compositional coordinate | Dimensionless ratio | CONDITIONAL PASS | only if explicitly used |
| `X,Y` | Ternary projection coordinates | Dimensionless projection coordinates | PASS | visualization geometry |
| `d_B,d_E` | Distance metrics | Dimensionless | PASS | no physical length scale |
| `H(b)` | Shannon entropy | Bits with log2 | PASS / citation pending | mathematical entropy only |
| `Ψ` | Raphael wave/state symbol | Unknown | FAIL / pending | no source-defined dimension in package |
| `Φ` | Raphael field symbol | Unknown | FAIL / pending | no source-defined dimension in package |
| `g` | Metric/tension/gravity-like symbol | Unknown | FAIL / pending | must not mix metric and scalar tension |
| `R` | Radius/Ricci-like symbol | Unknown | FAIL / pending | risk of radius-curvature conflation |
| `L` | Likelihood/log/action/Lagrangian | Unknown | FAIL / pending | action has physical dimensions; likelihood does not |
| `D_μ` | Covariant derivative | Unknown | FAIL / pending | requires manifold, coordinate, and connection definitions |

## Dimensional conclusion

The TPW core is dimensionally consistent because it is finite, discrete, and dimensionless.

The Raphael physical layer is not dimensionally accepted in this build. It remains blocked until exact equations, dimensions, and coefficient origins are specified.
