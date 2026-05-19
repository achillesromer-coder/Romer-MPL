# Romer-MPL Output Contract

## Purpose

Romer-MPL should convert large analysis outputs into compact, decision-ready forms.

## Permanent function

MPL is treated as Maximum Probable Loss. It may use GMAT and mission-planning support, but its ongoing purpose is risk, range and loss-envelope analysis.

## Preferred output types

- risk ranges
- loss envelopes
- disposition summaries
- route-burden summaries
- launch-window summaries
- recommended next configurations
- Sheets-ready compact rows
- public-safe summary reports where approved

## Avoid

- raw result overload in Sheets
- public display of unreviewed assumptions
- ambiguous route or source status

## Output flow

```text
Romer-MPL models
  -> compact analysis output
  -> LightSpeed Desktop review/compaction
  -> Sheets-ready rows
  -> Data W5 display
  -> Operations W5 workspace
```
