import json, sys

SP = '/private/tmp/claude-501/-Users-dags/6fcf10ff-db90-4cfe-b1dd-f1fbf02b2987/scratchpad/'
F = '/Users/dags/Desktop/Job Search Materials/Portfolio & Tracker/Job Tracker - July 2026.html'

html = open(F, encoding='utf-8').read()

CSS_ADD = """.hidden{display:none!important}
.days{font-family:var(--mono);font-size:10.5px;font-weight:700;border-radius:6px;padding:3px 7px;white-space:nowrap}
.d-ok{background:var(--a-bg);color:var(--a)}.d-mid{background:var(--c-bg);color:var(--c)}.d-old{background:var(--d-bg);color:var(--d)}
.vb{font-family:var(--mono);font-size:9.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;border-radius:6px;padding:3px 7px;white-space:nowrap}
.v-live{background:var(--a-bg);color:var(--a)}.v-unc{background:var(--c-bg);color:var(--c)}.v-net{background:var(--b-bg);color:var(--b)}
.rk{font-family:var(--mono);font-size:11px;color:var(--muted);font-weight:600}
.newtag{font-family:var(--mono);font-size:9px;font-weight:800;letter-spacing:.08em;color:var(--accent);background:var(--accent-soft);border-radius:5px;padding:3px 6px;white-space:nowrap}
.ainp{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:6px 9px;color:var(--ink);font-family:var(--sans);font-size:12.5px;transition:.15s}
.a-notes{width:100%}
.ainp:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
tr.arow>td{padding:9px 12px;border-bottom:1px solid var(--line2);vertical-align:middle;background:var(--surface)}
.onote{font-family:var(--mono);font-size:10.5px;color:var(--faint);padding:12px 2px 0;line-height:1.6}"""

VIEWS_ADD = """<div id="v-method" class="hidden"><div class="wrap"><div class="method" id="methodrows"></div></div></div>
<div id="v-apps" class="hidden"><div class="toolbar"><div class="wrap"><span class="lbl">Pipeline &middot; everything with a status, across Rankings and Openings</span><span class="count" id="acount"></span></div></div><main><div class="wrap" id="appsbody"></div></main></div>
<div id="v-openings" class="hidden"><div class="toolbar"><div class="wrap">
<input class="search" id="oq" placeholder="Search openings — company, role, notes…" autocomplete="off">
<div class="chips" id="ocity"></div><div class="chips" id="olane"></div>
<select class="chip" id="over"><option value="">All verification</option><option value="live">Live &middot; verified</option><option value="unc">Unconfirmed</option><option value="net">Network play</option></select>
<button class="chip" id="onew">New only</button><span class="count" id="ocount"></span>
</div></div><main><div class="wrap"><div class="onote">Openings database &middot; swept July 2026 across five lanes &times; NYC / London / SF / LA / Austin &middot; full dataset embedded in this file — filters change the view, not the file &middot; set a status here and it flows into Applications</div><table id="otbl"><thead><tr><th data-ok="company">Company<span class="ar"></span></th><th data-ok="lane" class="hide-sm">Lane<span class="ar"></span></th><th data-ok="city">Location<span class="ar"></span></th><th data-ok="comp" class="hide-sm">Comp<span class="ar"></span></th><th data-ok="verified">Verified<span class="ar"></span></th><th data-ok="ranked">Rank<span class="ar"></span></th><th data-ok="status">Status<span class="ar"></span></th><th></th></tr></thead><tbody id="orows"></tbody></table></div></main></div>"""

DATA_ADD = """const DLBASE='file:///Users/dags/Downloads/';
const OPENINGS=__OPENINGS__;
(function(){const RM={};R.forEach(r=>RM[(r.company+'|||'+r.role).toLowerCase()]=r);OPENINGS.forEach(o=>{const m=RM[(o.company+'|||'+o.role).toLowerCase()];if(m){o.company=m.company;o.role=m.role;o.status=m.status;}else{o.status='Not started';}});})();
const NEWOPEN=OPENINGS.filter(o=>o.ranked==null),ALLR=R.concat(NEWOPEN);"""

STATS_OLD = """function refreshStats(){const sc={};R.forEach(r=>{const s=stOf(r);sc[s]=(sc[s]||0)+1});
  el('updated').textContent=`${R.length} roles · ${Object.keys(DOCS).length} with résumé · progress saves automatically`;"""
STATS_NEW = """function refreshStats(){const sc={};ALLR.forEach(r=>{const s=stOf(r);sc[s]=(sc[s]||0)+1});
  el('updated').textContent=`${R.length} ranked · ${OPENINGS.length} openings in database · ${Object.keys(DOCS).length} with résumé · progress saves automatically`;"""

JS_ADD = """/* ===== Applications view ===== */
const APPORDER=['Offer','Interviewing','Applied','Researching','Rejected','Pass'];
function daysPill(dt){if(!dt)return '<span class="meta">—</span>';const d=Math.max(0,Math.floor((Date.now()-new Date(dt+'T00:00:00'))/864e5));const cl=d<=7?'d-ok':(d<=14?'d-mid':'d-old');return `<span class="days ${cl}">${d}d</span>`;}
function renderApps(){const rows=ALLR.filter(r=>stOf(r)!=='Not started');el('acount').textContent=rows.length+' tracked';
  if(!rows.length){el('appsbody').innerHTML='<div class="empty"><div class="eb">Nothing tracked yet — set a status on any role in Rankings or Openings and it appears here.</div></div>';return;}
  const map={};rows.forEach(r=>{const s=stOf(r);(map[s]=map[s]||[]).push(r);});
  let html='<table><thead><tr><th style="width:1%">Status</th><th>Company</th><th class="hide-sm">Track</th><th>Location</th><th>Applied</th><th></th><th class="hide-sm" style="width:32%">Next step / notes</th><th></th></tr></thead><tbody>';
  APPORDER.forEach(s=>{const g=map[s];if(!g)return;g.sort((a,b)=>(rec(b).date||'').localeCompare(rec(a).date||''));
    html+=`<tr class="grp"><td colspan="8"><div class="ghead"><span class="gname">${esc(s)}</span><span class="gc">${g.length}</span><span class="gline"></span></div></td></tr>`;
    g.forEach(r=>{const dk=esc(keyOf(r));const d=DOCS[keyOf(r)]||{};
      html+=`<tr class="arow"><td class="c-status"><select class="qstat a-stat p-${slug(s)}" data-key="${dk}">${STATUSES.map(o=>`<option ${o===s?'selected':''}>${esc(o)}</option>`).join('')}</select></td>`
      +`<td><div class="co">${esc(r.company)}${d.resume?' <span class="doc-i" title="résumé attached">📄</span>':''}</div><div class="ro">${esc(r.role)}</div></td>`
      +`<td class="hide-sm meta">${esc(r.track)}</td><td class="meta">${esc(r.city||r.loc)}</td>`
      +`<td><input type="date" class="ainp a-date" data-key="${dk}" value="${esc(rec(r).date||'')}"></td>`
      +`<td>${daysPill(rec(r).date)}</td>`
      +`<td class="hide-sm"><input type="text" class="ainp a-notes" data-key="${dk}" value="${esc(rec(r).notes||'')}" placeholder="Referral, contact, follow-up…"></td>`
      +`<td>${r.link?`<a class="lk" href="${esc(r.link)}" target="_blank" rel="noopener">↗</a>`:''}</td></tr>`;});});
  el('appsbody').innerHTML=html+'</tbody></table>';
  document.querySelectorAll('.a-stat').forEach(sl=>sl.onchange=e=>{const k=e.target.dataset.key;LS[k]=LS[k]||{};LS[k].status=e.target.value;if(e.target.value==='Applied'&&!LS[k].date)LS[k].date=new Date().toISOString().slice(0,10);save();celebrate(e.target.value);refreshStats();renderApps();});
  document.querySelectorAll('.a-date').forEach(i=>i.onchange=e=>{const k=e.target.dataset.key;LS[k]=LS[k]||{};LS[k].date=e.target.value;save();renderApps();});
  document.querySelectorAll('.a-notes').forEach(i=>i.onchange=e=>{const k=e.target.dataset.key;LS[k]=LS[k]||{};LS[k].notes=e.target.value;save();});}
/* ===== Openings database ===== */
const laneCount=OPENINGS.reduce((m,o)=>(m[o.lane]=(m[o.lane]||0)+1,m),{});
const ocityCount=OPENINGS.reduce((m,o)=>(m[o.city]=(m[o.city]||0)+1,m),{});
let ost={q:'',cities:new Set(),lanes:new Set(),ver:'',newonly:false,sort:'company',dir:1,open:new Set()};
el('ocity').innerHTML=['NYC','London','SF','LA','Austin','Remote','Other'].filter(c=>ocityCount[c]).map(c=>`<button class="chip" data-oc="${esc(c)}">${esc(c)} · ${ocityCount[c]}</button>`).join('');
el('olane').innerHTML=Object.keys(laneCount).sort((a,b)=>laneCount[b]-laneCount[a]).map(l=>`<button class="chip" data-ol="${esc(l)}">${esc(l)} · ${laneCount[l]}</button>`).join('');
document.querySelectorAll('#ocity .chip').forEach(c=>c.onclick=()=>{const v=c.dataset.oc;ost.cities.has(v)?ost.cities.delete(v):ost.cities.add(v);c.classList.toggle('on');renderOpen();});
document.querySelectorAll('#olane .chip').forEach(c=>c.onclick=()=>{const v=c.dataset.ol;ost.lanes.has(v)?ost.lanes.delete(v):ost.lanes.add(v);c.classList.toggle('on');renderOpen();});
el('oq').oninput=e=>{ost.q=e.target.value.toLowerCase();renderOpen();};
el('over').onchange=e=>{ost.ver=e.target.value;renderOpen();};
el('onew').onclick=()=>{ost.newonly=!ost.newonly;el('onew').classList.toggle('on',ost.newonly);renderOpen();};
document.querySelectorAll('#otbl th[data-ok]').forEach(th=>th.onclick=()=>{const k=th.dataset.ok;if(ost.sort===k)ost.dir*=-1;else{ost.sort=k;ost.dir=1;}renderOpen();});
function vKind(v){return (v||'').indexOf('live')===0?'live':((v||'').indexOf('network')>=0?'net':'unc');}
function vBadge(v){const k=vKind(v);return `<span class="vb v-${k}">${k==='live'?'Live':(k==='net'?'Network':'Verify')}</span>`;}
function omatch(o){if(ost.cities.size&&!ost.cities.has(o.city))return false;if(ost.lanes.size&&!ost.lanes.has(o.lane))return false;if(ost.ver&&vKind(o.verified)!==ost.ver)return false;if(ost.newonly&&o.ranked!=null)return false;
  if(ost.q){const h=(o.company+' '+o.role+' '+o.track+' '+o.loc+' '+o.lane+' '+o.comp+' '+(o.fit||'')+' '+(o.edge||'')+' '+(rec(o).notes||'')).toLowerCase();if(!h.includes(ost.q))return false;}return true;}
function renderOpen(){let rows=OPENINGS.filter(omatch);const k=ost.sort,d=ost.dir;
  rows.sort((a,b)=>{let x=k==='status'?stOf(a):(k==='ranked'?(a.ranked==null?999:a.ranked):a[k]),y=k==='status'?stOf(b):(k==='ranked'?(b.ranked==null?999:b.ranked):b[k]);if(typeof x==='string'){x=x.toLowerCase();y=(y||'').toLowerCase();}if(x<y)return -d;if(x>y)return d;return 0;});
  el('ocount').textContent=rows.length+' of '+OPENINGS.length;
  document.querySelectorAll('#otbl th .ar').forEach(a=>a.textContent='');const tha=document.querySelector(`#otbl th[data-ok="${k}"] .ar`);if(tha)tha.textContent=d>0?' ▲':' ▼';
  if(!rows.length){el('orows').innerHTML='<tr><td colspan="8"><div class="empty"><div class="eb">Nothing matches these filters.</div></div></td></tr>';return;}
  let html='';rows.forEach(o=>{const id=OPENINGS.indexOf(o);const s=stOf(o);const dk=esc(keyOf(o));const open=ost.open.has(id);
    html+=`<tr class="role orole ${open?'open':''}" data-oid="${id}"><td><div class="co">${esc(o.company)}</div><div class="ro">${esc(o.role)}</div></td>`
    +`<td class="hide-sm meta">${esc(o.lane)}</td><td class="meta">${esc(o.loc)}</td><td class="hide-sm meta">${esc(o.comp)}</td>`
    +`<td>${vBadge(o.verified)}</td>`
    +`<td>${o.ranked!=null?`<span class="rk">#${o.ranked}</span>`:'<span class="newtag">NEW</span>'}</td>`
    +`<td class="c-status"><select class="qstat o-stat p-${slug(s)}" data-key="${dk}" onclick="event.stopPropagation()">${STATUSES.map(x=>`<option ${x===s?'selected':''}>${esc(x)}</option>`).join('')}</select></td>`
    +`<td class="c-chev"><span class="chev">›</span></td></tr>`;
    if(open)html+=`<tr class="detail"><td colspan="8"><div class="panel">`
      +(o.fit?`<p class="why">${esc(o.fit)}</p>`:'')
      +(o.edge?`<div class="nxt">Edge — ${esc(o.edge)}</div>`:'')
      +`<div class="nxt" style="margin-bottom:14px">${esc(o.verified)}${o.ranked!=null?` · ranked #${o.ranked} in Rankings tab`:' · not yet ranked'}</div>`
      +`<div class="links">${o.link?`<a class="lk lk-primary" href="${esc(o.link)}" target="_blank" rel="noopener">Apply ↗</a>`:''}<a class="lk lk-in" href="https://www.linkedin.com/search/results/companies/?keywords=${encodeURIComponent(o.company)}" target="_blank" rel="noopener">in LinkedIn ↗</a><a class="lk" href="https://www.google.com/search?q=${encodeURIComponent(o.company+' careers')}" target="_blank" rel="noopener">Company ↗</a></div>`
      +`<div class="track"><div class="fld"><label>Applied date</label><input type="date" class="o-date" data-key="${dk}" value="${esc(rec(o).date||'')}"></div>`
      +`<div class="fld wide"><label>Notes</label><textarea class="o-notes" data-key="${dk}" placeholder="Referral, contact, follow-up…">${esc(rec(o).notes||'')}</textarea></div></div>`
      +`</div></td></tr>`;});
  el('orows').innerHTML=html;
  document.querySelectorAll('#orows tr.orole').forEach(tr=>tr.onclick=()=>{const id=+tr.dataset.oid;ost.open.has(id)?ost.open.delete(id):ost.open.add(id);renderOpen();});
  document.querySelectorAll('#orows tr.detail>td').forEach(td=>td.onclick=e=>e.stopPropagation());
  document.querySelectorAll('.o-stat').forEach(sl=>sl.onchange=e=>{const k2=e.target.dataset.key;LS[k2]=LS[k2]||{};LS[k2].status=e.target.value;if(e.target.value==='Applied'&&!LS[k2].date)LS[k2].date=new Date().toISOString().slice(0,10);save();celebrate(e.target.value);refreshStats();renderOpen();});
  document.querySelectorAll('.o-date').forEach(i=>i.onchange=e=>{const k2=e.target.dataset.key;LS[k2]=LS[k2]||{};LS[k2].date=e.target.value;save();});
  document.querySelectorAll('.o-notes').forEach(i=>i.onchange=e=>{const k2=e.target.dataset.key;LS[k2]=LS[k2]||{};LS[k2].notes=e.target.value;save();});}
</script>"""

reps = [
    ('.hidden{display:none!important}', CSS_ADD),
    ('<div class="tabs"><button class="tab active" data-view="rankings">Rankings</button><button class="tab" data-view="network">Network Plays</button><button class="tab" data-view="method">Methodology</button></div>',
     '<div class="tabs"><button class="tab active" data-view="rankings">Rankings</button><button class="tab" data-view="apps">Applications</button><button class="tab" data-view="openings">Openings</button><button class="tab" data-view="network">Network Plays</button><button class="tab" data-view="method">Methodology</button></div>'),
    ('<div id="v-method" class="hidden"><div class="wrap"><div class="method" id="methodrows"></div></div></div>', VIEWS_ADD),
    ("const DLBASE='file:///Users/dags/Downloads/';", DATA_ADD),
    (STATS_OLD, STATS_NEW),
    ("document.querySelectorAll('tr.grp').forEach", "document.querySelectorAll('#rows tr.grp').forEach"),
    ("document.querySelectorAll('tr.role').forEach", "document.querySelectorAll('#rows tr.role').forEach"),
    ("document.querySelectorAll('tr.detail>td').forEach", "document.querySelectorAll('#rows tr.detail>td').forEach"),
    ("document.querySelectorAll('.qstat').forEach", "document.querySelectorAll('#rows .qstat').forEach"),
    ("document.querySelectorAll('.f-date').forEach", "document.querySelectorAll('#rows .f-date').forEach"),
    ("document.querySelectorAll('.f-notes').forEach", "document.querySelectorAll('#rows .f-notes').forEach"),
    ("['rankings','network','method'].forEach(v=>el('v-'+v).classList.toggle('hidden',v!==t.dataset.view));});",
     "['rankings','apps','openings','network','method'].forEach(v=>el('v-'+v).classList.toggle('hidden',v!==t.dataset.view));if(t.dataset.view==='apps')renderApps();if(t.dataset.view==='openings')renderOpen();});"),
    ('</script>', JS_ADD),
]

for old, new in reps:
    n = html.count(old)
    if n != 1:
        sys.exit(f'ANCHOR FAIL ({n}x): {old[:80]}')
    html = html.replace(old, new)

openings = json.dumps(json.load(open(SP + 'openings_merged.json')), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert html.count('__OPENINGS__') == 1
html = html.replace('__OPENINGS__', openings)

open(F, 'w', encoding='utf-8').write(html)

# extract inline script for syntax check
s = html.index('<script>') + 8
e = html.index('</script>')
open(SP + 'check_script.js', 'w', encoding='utf-8').write(html[s:e])
print('patched OK ·', len(html), 'bytes')
