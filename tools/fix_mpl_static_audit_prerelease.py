#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'tools/mpl_static_audit.py')
s=p.read_text(encoding='utf-8')
old='r"sourceHash|source_hash|modelHash|model_hash|commitSha|commit_sha"'
new='r"sourceHash|source_hash|modelHash|model_hash|commitSha|commit_sha|parentSourceSha256|runtimeHash"'
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('provenance detector anchor not found')
p.write_text(s,encoding='utf-8')
print('static audit provenance detector aligned with pre-release receipts')
