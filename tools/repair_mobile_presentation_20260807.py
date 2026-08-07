from pathlib import Path

path=Path('index.html')
source=path.read_text(encoding='utf-8')
original=source
marker='/* MPL RESPONSIVE GLOBE HOTFIX — 2026-08-07 */'

if marker not in source:
    css=r'''
/* MPL RESPONSIVE GLOBE HOTFIX — 2026-08-07 */
@media (max-width:760px) {
  .topbar { padding:0 10px; }
  .tb-mission,.tb-sep,.utc-clock { display:none; }
  .main { position:relative; }
  .panel-wrap {
    position:absolute !important; inset:0 auto 0 0;
    width:min(300px,84vw); height:100%; z-index:45;
    pointer-events:none;
  }
  .panel-wrap .panel {
    width:100%; height:100%; pointer-events:auto;
    box-shadow:18px 0 48px rgba(0,0,0,.38);
  }
  .panel-collapse-btn { pointer-events:auto; }
  .panel-wrap:has(.panel.collapsed) .panel-collapse-btn { right:auto; left:0; }
  .globe-wrap { flex:1 1 100%; width:100%; height:100%; }
  .view-toggles { top:8px; right:8px; max-width:calc(100vw - 20px); }
  .view-btn { padding:5px 8px; font-size:9px; }
  .globe-legend { top:48px; right:8px; max-width:calc(100vw - 20px); }
  .globe-ctrl { left:8px; bottom:66px; }
  .zoom-indicator { right:8px; bottom:66px; }
  .compass { right:48px; bottom:72px; }
  #globe-hint,.kbd-hints { display:none; }
  .telebar { height:48px; padding:0 8px; overflow-x:auto; scrollbar-width:none; }
  .telebar::-webkit-scrollbar { display:none; }
  .tele-item { padding:0 8px; flex:0 0 auto; }
  .tele-right { position:sticky; right:0; flex:0 0 auto; padding-left:8px; background:var(--bg1); }
  .tele-btn { white-space:nowrap; }
}
@media (max-width:520px) {
  .tb-version { display:none; }
  .tb-logo { font-size:11px; }
  .live-badge { padding:3px 7px; font-size:8px; }
  .icon-btn { width:28px; height:28px; }
  .panel-wrap { width:min(300px,88vw); }
  .view-btn { padding:5px 6px; font-size:8px; }
  .tele-item:nth-child(2),.tele-item:nth-child(5),.tele-item:nth-child(6) { display:none; }
}
'''
    source=source.replace('</style>',css+'\n</style>',1)

# Present the globe first on narrow screens while retaining the left-edge panel handle.
needle="document.getElementById('app')?.classList.add('live');"
addition="""document.getElementById('app')?.classList.add('live');
    if(window.matchMedia?.('(max-width:760px)').matches && !S.panelCollapsed) {
      setTimeout(()=>togglePanel(), 180);
    }"""
if needle in source and addition not in source:
    source=source.replace(needle,addition,1)

if source!=original:
    path.write_text(source,encoding='utf-8')
    print('Applied responsive globe presentation repair.')
else:
    print('Responsive globe presentation repair already applied.')
