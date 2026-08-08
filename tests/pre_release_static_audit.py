from pathlib import Path
from html.parser import HTMLParser
import collections, hashlib, json, re, sys

path=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
source=path.read_text(encoding='utf-8')

class DocumentAudit(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.handlers=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if values.get('id'): self.ids.append(values['id'])
        for key,value in attrs:
            if key.startswith('on') and value: self.handlers.append((key,value))

parser=DocumentAudit(); parser.feed(source)
ids=set(parser.ids)
functions=re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(',source)
known_functions=set(functions)
static_refs=set(re.findall(r"getElementById\(\s*['\"]([^'\"]+)['\"]\s*\)",source))
handler_calls=set()
for _,handler in parser.handlers:
    handler_calls.update(re.findall(r'\b([A-Za-z_$][\w$]*)\s*\(',handler))
handler_ignore={'parseFloat','Number','String','Math','setTimeout','getElementById','toFixed','if'}

checks={
    'duplicate_ids':[k for k,v in collections.Counter(parser.ids).items() if v>1],
    'duplicate_functions':[k for k,v in collections.Counter(functions).items() if v>1],
    'missing_static_ids':sorted(static_refs-ids),
    'missing_inline_handlers':sorted(x for x in handler_calls-known_functions-handler_ignore if not x.startswith('document')),
    'unfinished_markers':re.findall(r'(?i)\b(?:TODO|FIXME|TBD|WIP)\b',source),
    'semantic_version_markers':re.findall(r'(?i)\bv\d+\.\d+(?:\.\d+)?\b|data-version\s*=|modelVersion',source),
    'legacy_numbered_tabs':re.findall(r"\b(?:00|01|02|03|04|05|06|07|08|09)_(?:MPL_Config|Vehicles|Launch_Sites|High_Value_Assets|MPL_Constants|GDP_Table|Population_Zones|Failure_Modes|Operators|BRIDGE_W5_Targets)\b",source),
    'read_sheet_tab':re.findall(r'\breadSheetTab\b',source),
    'no_cors':re.findall(r'no-cors',source,re.I),
    'external_ai':re.findall(r'anthropic|claude',source,re.I),
    'compliance_claim':re.findall(r'\bcompliance\b',source,re.I),
    'insurance_claim':re.findall(r'\binsurance\b',source,re.I),
    'embedded_tle_lines':re.findall(r'\n[12] \d{5}[A-Z ]',source),
}
assertions={
    'one_calculate_mpl':len(re.findall(r'function\s+calculateMPL\s*\(',source))==1,
    'one_transit_registry':len(re.findall(r'const\s+TRANSITS\s*=',source))==1,
    'one_failure_registry':len(re.findall(r'const\s+FMODES\s*=',source))==1,
    'one_webgl_context_loss_listener':source.count("addEventListener('webglcontextlost'")==1,
    'minimum_camera_altitude_1km':'minAltitudeKm: 1' in source and 'MIN_CAMERA_ALTITUDE_KM":1' in source,
    'radial_hard_surface_guard':'camera.position.length() < radiusAtAltitudeKm(CAMERA_LIMITS.minAltitudeKm)' in source,
    'surface_overlays_below_floor':all(token in source for token in ['riskHeat:0.14','iip:0.15','reentry:0.16','debris:0.18']),
    'controlled_snapshot':'CONTROLLED_WORKBOOK_SNAPSHOT' in source and 'WORKBOOK_SNAPSHOT' in source,
    'regulatory_boundary':'impactIsopleth10e7:false' in source and "hvaScreeningMethod:'ROMER_SCREENING_HEURISTIC'" in source,
    'pre_release_identity':'PRE_RELEASE' in source and 'Pre-release' in source,
}
failures={k:v for k,v in checks.items() if v}
failures.update({k:v for k,v in assertions.items() if not v})
receipt={
    'sha256':hashlib.sha256(source.encode()).hexdigest(),'bytes':len(source.encode()),'line_count':source.count('\n')+1,
    'checks':{k:len(v) for k,v in checks.items()},'assertions':assertions,'failures':failures
}
print(json.dumps(receipt,indent=2,ensure_ascii=False))
if failures: raise SystemExit(2)
