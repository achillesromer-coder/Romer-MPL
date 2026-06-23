# RAP-001 — Canonical Equation Register

Version: v1_1 governance build  
Date: 2026-06-24

| Eq ID | Name | Equation | Variables | Proof class | Dimensional status | Claim status |
|---|---|---|---|---:|---|---|
| EQ-TPW-001 | One-dimensional support | `k ∈ {2,...,12}` | `k` | P0 | Dimensionless integer | LOCKED |
| EQ-TPW-002 | Dice-sum count function | `W(k)=6-|7-k|` | `k,W` | P0/P1 | Count | LOCKED |
| EQ-TPW-003 | One-dimensional PMF | `P(X_i=k)=W(k)/36` | `Xi,k,W` | P1 | Dimensionless probability | LOCKED |
| EQ-TPW-004 | Product state | `x=(x1,x2,x3) ∈ {2,...,12}^3` | `x` | P0 | Dimensionless integer vector | LOCKED |
| EQ-TPW-005 | Joint weight | `W(x)=W(x1)W(x2)W(x3)` | `x,W` | P1 | Count-product | LOCKED |
| EQ-TPW-006 | Joint probability | `P(x)=W(x)/36^3` | `x,W,P` | P1/P2 | Dimensionless probability | LOCKED |
| EQ-TPW-007 | Normalization | `Σ_x P(x)=1` | `P,Ω` | P1/P2 | Dimensionless | LOCKED |
| EQ-TPW-008 | Maximum state | `argmax_x P(x)=(7,7,7)` | `P,x` | P1/P2 | Dimensionless | LOCKED |
| EQ-GEO-001 | Raw-sum total | `S=x1+x2+x3` | `S,x_i` | P1 | Dimensionless scalar | LOCKED |
| EQ-GEO-002 | Raw barycentric coordinate | `b_i=x_i/S` | `b_i,x_i,S` | P1/P3 | Dimensionless coordinate | LOCKED |
| EQ-GEO-003 | Raw barycentric closure | `b1+b2+b3=1` | `b_i` | P1/P2 | Dimensionless | LOCKED |
| EQ-GEO-004 | Weight-compositional coordinate | `q_i=W(x_i)/(W(x1)+W(x2)+W(x3))` | `q_i,W` | P1/P3 | Dimensionless coordinate | CONDITIONAL |
| EQ-GEO-005 | Ternary projection | `X=0.5*b1+b3`, `Y=(√3/2)*b1` | `X,Y,b` | P1/P3 | Dimensionless projection | LOCKED |
| EQ-GEO-006 | Barycentric distance | `d_B^2=Σ_i(b_i-1/3)^2` | `d_B,b_i` | P1/P3 | Dimensionless | LOCKED |
| EQ-GEO-007 | Projection distance identity | `d_E^2=(1/2)d_B^2` | `d_E,d_B` | P1/P2 | Dimensionless | LOCKED |
| EQ-ENT-001 | Composition entropy | `H(b)=-Σ_i b_i log2(b_i)` | `H,b_i` | P1 | Bits | CITATION-PENDING |
| EQ-N-001 | Finite independent product schema | `P(x_1,...,x_N)=∏_i p_i(x_i)` | `N,p_i,x_i` | P1 | Dimensionless probability | CONDITIONAL |
| EQ-RAP-001 | Raphael wave/state equation placeholder | `PENDING SOURCE TRANSCRIPTION` | `Ψ` | P5 | Pending | NOT ACCEPTED |
| EQ-RAP-002 | Raphael field equation placeholder | `PENDING SOURCE TRANSCRIPTION` | `Φ,g,D_μ` | P5 | Pending | NOT ACCEPTED |
| EQ-RAP-003 | Physical correspondence equation placeholder | `PENDING DIMENSIONAL AUDIT` | mixed | P5 | Pending | NOT ACCEPTED |

## Register rule

No Raphael-side equation may be promoted above `P5` until exact source transcription is complete, variables are defined in RAP-001A, units pass RAP-002, coefficients pass RAP-003, correspondence class is assigned in RAP-004, and a falsification condition is entered in NBT-001.
