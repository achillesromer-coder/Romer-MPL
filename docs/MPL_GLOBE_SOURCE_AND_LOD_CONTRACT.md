# MPL Globe Source and LOD Contract

## Purpose

This document defines the operational rendering/source contract for the Römer MPL Engine globe. It separates visual cartography from MPL model evidence and makes the 1 km camera-floor behaviour machine- and human-readable.

## Camera and geometry contract

- Reference Earth radius: `6371.0 km`.
- Minimum camera altitude: `1 km` above the reference radius.
- The 1 km floor is a Römer rendering/collision invariant, not an Australian Space Agency requirement.
- The near-surface imagery shell is `0.012 km` above the reference surface.
- MPL overlays remain above the imagery shell and below the camera floor: data `0.04 km`, graticule `0.06 km`, HVA `0.08 km`, corridor `0.10 km`, site `0.12 km`, risk heat `0.14 km`, IIP `0.15 km`, re-entry `0.16 km`, debris `0.18 km`.
- Cloud and atmospheric shells are suppressed during close approach so the camera cannot enter or clip through those visual layers.
- Perspective near clipping is recalculated from physical camera altitude to preserve depth precision at 1 km.

## Global deterministic layer

The always-available globe is generated in-document from Natural Earth vector data and the Römer cartographic palette. Natural Earth is intentionally treated as a small-scale/global cartographic source, not as metre-scale ground imagery.

Source: https://www.naturalearthdata.com/

Natural Earth publishes 1:10m, 1:50m and 1:110m data. The 1:10m product is the most detailed Natural Earth scale and is described by its publisher as suitable for zoomed-in maps of countries and regions; it is not represented by MPL as 1 km ground-resolution imagery.

## Adaptive near-surface layer

At camera altitude `<= 300 km`, the engine requests a local curved imagery patch from NASA Global Imagery Browse Services (GIBS):

- Service: NASA GIBS WMS, EPSG:4326.
- Endpoint: `https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi`.
- Layer: `BlueMarble_NextGeneration`.
- Source product resolution recorded by NASA: `500 m` full-resolution tiled imagery.
- Request size: `2048 x 2048` at `<= 50 km`, `1536 x 1536` at `<= 150 km`, `1024 x 1024` through the remainder of the near-surface band.
- Spatial footprint: derived from the physical visible-horizon cap and overscanned by `1.28`, rather than magnifying a global raster.
- Patch refresh: throttled by movement of camera nadir relative to the current patch footprint.
- Exit hysteresis: patch remains eligible until `360 km` to prevent rapid LOD flicker around the entry boundary.

NASA GIBS access documentation: https://nasa-gibs.github.io/gibs-api-docs/access-basics/

NASA Blue Marble Next Generation source description: https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-map/

## Failure and fallback contract

NASA GIBS is external visual enrichment. It is never required for MPL calculations, model evidence, mission logging or regulatory screening logic.

If a GIBS request fails, times out, returns non-image content or is unavailable:

1. the local imagery state changes to `ERROR`;
2. the UI exposes `LOCAL DETAIL UNAVAILABLE · CONTROLLED GLOBAL`;
3. the deterministic Natural Earth globe remains rendered and interactive;
4. MPL overlays and calculations remain unchanged.

No fabricated or stale local imagery is substituted.

## Regulatory boundary

Neither Natural Earth nor NASA Blue Marble imagery constitutes the Flight Safety Code `10^-7` probability-of-impact isopleth or application-grade hazard geometry. Both are cartographic/visual context. Regulatory-parity HVA inclusion remains dependent on independently derived controlled hazard geometry and specialist validation.

## Browser acceptance

`tests/near_surface_lod_probe.mjs` verifies under Chromium/WebGL that:

- the camera reaches exactly 1 km without penetrating the reference Earth surface;
- the local imagery patch is a child of the rotating globe and remains below MPL overlays;
- the NASA GIBS source identifier, 500 m source receipt and 2048-pixel close-range request contract are present;
- the near clipping plane remains valid at 1 km;
- the near-surface LOD exits cleanly above 360 km;
- a simulated NASA GIBS outage leaves the controlled global globe rendering;
- no page or console errors occur.
