# MPL Method and Visualization Boundary

## Controlled source basis

The active screening implementation is informed by the Australian Space Agency Maximum Probable Loss Methodology published 1 August 2019.

The methodology states that the Agency estimator is not a comprehensive MPL calculator, is not a substitute for independent specialist advice and its results cannot be used in an application. The Römer MPL Engine therefore remains a decision-support and screening artefact until independent validation is complete.

## Secondary casualties

For uprange mishaps, the methodology directs the calculation of secondary casualties using 1.5 times rounded primary casualties, with the secondary value rounded upward and added to the primary casualty count. Secondary effects do not apply to downrange or return mishaps under the methodology's stated assumptions.

## High-value assets and hazard geometry

Regulatory-parity HVA inclusion depends on Flight Safety Code risk-hazard analysis and the 10^-7 probability-of-impact isopleth. The current Römer azimuth/distance weighting does not create that isopleth and must not be represented as one. It is explicitly tagged `ROMER_SCREENING_HEURISTIC` in runtime evidence.

## Globe camera

The Agency methodology does not prescribe an interactive globe-camera minimum altitude. Römer therefore uses a 1 km minimum camera altitude solely as a visualization/rendering invariant. It prevents the camera from crossing the model Earth surface and is not used as an MPL calculation threshold or regulatory claim.

The camera transformation is:

`camera radius = 1 + altitude_km / 6371.0088`

with a 1 km floor, 11,500 km reset altitude and 80 km launch-site focus altitude.

## Public data boundary

The anonymous static browser uses a controlled embedded snapshot. Browser-to-Apps-Script reads are not relied upon because the current endpoint does not provide a browser-acceptable CORS response. Apps Script remains a separate operator/write transport concern pending authenticated same-origin or controlled-snapshot architecture.