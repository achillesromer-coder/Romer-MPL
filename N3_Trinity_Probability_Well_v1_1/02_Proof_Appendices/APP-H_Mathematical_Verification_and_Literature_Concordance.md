# APP-H — Mathematical Verification and Literature Concordance

Version: v1_1 governance build  
Date: 2026-06-24

## H.1 One-dimensional dice-sum distribution

For the sum of two fair six-sided dice, the support is `{2,...,12}`. The count of ordered pairs producing sum `k` is:

```text
W(k)=6-|7-k|
```

for `k∈{2,...,12}`. The vector is `[1,2,3,4,5,6,5,4,3,2,1]`, and `Σ_k W(k)=36`.

## H.2 Three-variable product space

For three independent copies `X1, X2, X3`, the sum-state space is `{2,...,12}^3` and has `11^3=1331` states. The primitive ordered outcome count is `36^3=46656`.

## H.3 Joint probability and normalization

For state `x=(x1,x2,x3)`:

```text
P(x)=W(x1)W(x2)W(x3)/36^3
```

Then:

```text
Σ_x P(x) = (Σ_k W(k)/36)^3 = (36/36)^3 = 1
```

The validation report confirms the sum exactly as `1/1`.

## H.4 Maximum-probability state

`W(k)` is uniquely maximized at `k=7`, with `W(7)=6`. Therefore the product `W(x1)W(x2)W(x3)` is uniquely maximized at `(7,7,7)`, with:

```text
P(7,7,7)=6^3/36^3=216/46656=1/216
```

## H.5 Simplex embedding

Define:

```text
S=x1+x2+x3
b_i=x_i/S
```

Since each `xi>0`, each `b_i>0`, and `b1+b2+b3=1`, the vector `b=(b1,b2,b3)` lies in the closed two-simplex. This is a compositional coordinate, not the joint probability.

## H.6 Non-injectivity of simplex mapping

If `x=(a,a,a)`, then `b=(1/3,1/3,1/3)` for all `a∈{2,...,12}`. Hence the raw-triple to simplex-coordinate map is non-injective. The validation report confirms `unique normalized points = 1141 < 1331`.

## H.7 Ternary projection and distance identity

Using `X=0.5*b1+b3` and `Y=(√3/2)*b1`, and defining `d_B^2=Σ_i(b_i-1/3)^2`, the equilateral ternary projection gives:

```text
d_E^2=(1/2)d_B^2
```

The validation report records maximum identity error `6.938893903907228e-17`.

## H.8 Entropy clarification

For a composition:

```text
H(b)=-Σ_i b_i log2(b_i)
```

standard constrained entropy theory gives a maximum at `b=(1/3,1/3,1/3)` under `b1+b2+b3=1`. This does not by itself prove `TPW modal state = global entropy attractor`, because the TPW modal state is determined by product dice weights, while `H(b)` is a compositional entropy of normalized coordinates.

## H.9 Spiral negative result

No spiral is present in the unordered TPW state space as a raw theorem. A spiral arises only after an ordering, traversal, ring selection, or parameterization is imposed.

## H.10 Finite N-variable product-measure schema

For finite independent variables with normalized PMFs `p_i`:

```text
P(x1,...,xN)=∏_i p_i(x_i)
```

and:

```text
Σ_{x1,...,xN} P(x1,...,xN)=∏_i Σ_{xi} p_i(xi)=1
```

This is a valid finite product-measure generalization. It does not establish physical N-body mechanics.

## H.11 Literature concordance

| Topic | Required source linkage | Status |
|---|---|---|
| finite probability and dice enumeration | Feller / probability text | exact page pending |
| combinatorial counting | Aigner / combinatorics text | exact page pending |
| simplex and barycentric geometry | Coxeter / geometry reference | exact page pending |
| compositional simplex interpretation | Aitchison / compositional data reference | exact page pending |
| Shannon entropy | Shannon; Cover & Thomas | exact page pending |
| maximum entropy method | Jaynes | exact page pending |
| group action / orbit language | Dummit & Foote or equivalent | exact page pending |
| dimensional audit method | Buckingham-dimensional-analysis reference | exact page pending |
| isomorphism discipline | Mac Lane / algebraic structure reference | exact page pending |
| mechanics background | Goldstein only as background | exact page pending |

## H.12 Proof-lock conclusion

The TPW core is proof-ready as finite probability mathematics. The Raphael physical correspondence layer is not proof-locked and remains governed by RAP-004.
