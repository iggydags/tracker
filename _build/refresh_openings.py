#!/usr/bin/env python3
"""Refresh the Openings database inside 'Job Tracker - July 2026.html'.

Re-sweeps every Greenhouse / Ashby / Lever board already referenced in the
database, then:
  1. marks each existing ATS-linked opening 'live <Month Year>' or 'closed <Month Year>'
  2. appends NEW matching postings found on those same boards (tagged NEW in the UI)
  3. rewrites the HTML in place and syncs openings_merged.json

Usage:
  python3 refresh_openings.py            # verify + pull new roles
  python3 refresh_openings.py --verify-only   # only update live/closed, add nothing

Stdlib only. Non-ATS links (careers pages, aggregators) are left untouched.
"""
import json, re, sys, urllib.request, urllib.error
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = HERE.parent / 'Job Tracker - July 2026.html'
SYNC = HERE / 'openings_merged.json'

STAMP = date.today().strftime('%B %Y')          # e.g. 'July 2026'
UA = {'User-Agent': 'Mozilla/5.0 (job-tracker-refresh)'}

INCLUDE = re.compile(
    r'chief of staff|biz ?ops|business operations|strategy|strategic|operations analyst'
    r'|partnerships|business development|go.to.market|gtm|growth|market(s|ing)? operations'
    r'|finance|trading|investment|analyst|associate|activations', re.I)
EXCLUDE = re.compile(
    r'senior|staff |principal|director|vp |vice president|head of|lead,|intern|engineer'
    r'|developer|scientist|designer|recruiter|counsel|attorney|account executive|sales development', re.I)
CITY = re.compile(r'new york|nyc|london|austin|san francisco|bay area|remote', re.I)

GH = re.compile(r'(?:job-)?boards\.greenhouse\.io/([A-Za-z0-9_-]+)/jobs/(\d+)')
ASHBY = re.compile(r'jobs\.ashbyhq\.com/([A-Za-z0-9_-]+)/([0-9a-f-]{36})')
LEVER = re.compile(r'jobs\.lever\.co/([A-Za-z0-9_-]+)/([0-9a-f-]{36})')


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
            return json.loads(r.read().decode('utf-8', 'replace'))
    except Exception as e:
        print(f'  ! fetch failed {url} ({e})')
        return None


def fetch_board(kind, slug):
    """Return (ids:set[str], jobs:list[{id,title,loc,url}]) or None on failure."""
    if kind == 'gh':
        d = get(f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs')
        if d is None or 'jobs' not in d:
            return None
        jobs = [{'id': str(j['id']), 'title': j.get('title', ''),
                 'loc': (j.get('location') or {}).get('name', ''),
                 'url': j.get('absolute_url', '')} for j in d['jobs']]
    elif kind == 'ashby':
        d = get(f'https://api.ashbyhq.com/posting-api/job-board/{slug}')
        if d is None or 'jobs' not in d:
            return None
        jobs = [{'id': str(j.get('id', '')), 'title': j.get('title', ''),
                 'loc': j.get('location', '') or '',
                 'url': j.get('jobUrl', '') or f'https://jobs.ashbyhq.com/{slug}/{j.get("id","")}'}
                for j in d['jobs']]
    else:  # lever
        d = get(f'https://api.lever.co/v0/postings/{slug}?mode=json')
        if d is None or not isinstance(d, list):
            return None
        jobs = [{'id': str(j.get('id', '')), 'title': j.get('text', ''),
                 'loc': ((j.get('categories') or {}).get('location') or ''),
                 'url': j.get('hostedUrl', '')} for j in d]
    return {j['id'] for j in jobs}, jobs


def ats_ref(link):
    for kind, rx in (('gh', GH), ('ashby', ASHBY), ('lever', LEVER)):
        m = rx.search(link or '')
        if m:
            return kind, m.group(1), m.group(2)
    return None


def main():
    verify_only = '--verify-only' in sys.argv
    h = HTML.read_text(encoding='utf-8')
    m = re.search(r'const OPENINGS=(\[.*?\]);\n', h, re.S)
    if not m:
        sys.exit('OPENINGS array not found in HTML')
    openings = json.loads(m.group(1).replace('<\\/', '</'))

    # boards referenced in the database, and company/lane per board
    boards = {}          # (kind, slug) -> {'company':…, 'lane':…}
    for o in openings:
        ref = ats_ref(o.get('link', ''))
        if ref:
            boards.setdefault(ref[:2], {'company': o['company'], 'lane': o['lane']})
    print(f'{len(openings)} openings · {len(boards)} ATS boards to sweep')

    live, results = {}, {}
    for (kind, slug), meta in sorted(boards.items()):
        r = fetch_board(kind, slug)
        if r is None:
            continue
        results[(kind, slug)] = r
        print(f'  ✓ {kind}:{slug} — {len(r[0])} live postings ({meta["company"]})')

    # 1. verify existing
    n_live = n_closed = 0
    for o in openings:
        ref = ats_ref(o.get('link', ''))
        if not ref or ref[:2] not in results:
            continue
        ids = results[ref[:2]][0]
        if ref[2] in ids:
            o['verified'] = f'live {STAMP}'
            n_live += 1
        else:
            o['verified'] = f'closed {STAMP}'
            n_closed += 1

    # 2. new postings on the same boards
    added = []
    if not verify_only:
        have = {(o['company'].strip().lower(), o['role'].strip().lower()) for o in openings}
        have_ids = set()
        for o in openings:
            ref = ats_ref(o.get('link', ''))
            if ref:
                have_ids.add(ref[2])
        for (kind, slug), (ids, jobs) in results.items():
            meta = boards[(kind, slug)]
            for j in jobs:
                if j['id'] in have_ids:
                    continue
                t = j['title']
                if not INCLUDE.search(t) or EXCLUDE.search(t) or not CITY.search(j['loc'] or 'unknown'):
                    continue
                k = (meta['company'].strip().lower(), t.strip().lower())
                if k in have:
                    continue
                have.add(k)
                loc = j['loc'] or 'Not posted'
                l = loc.lower()
                city = ('NYC' if 'new york' in l or 'nyc' in l else
                        'London' if 'london' in l else
                        'Austin' if 'austin' in l else
                        'SF' if 'san francisco' in l or 'bay area' in l else
                        'Remote' if 'remote' in l else 'Other')
                added.append({'company': meta['company'], 'role': t, 'track': 'Auto-sweep',
                              'loc': loc, 'city': city, 'comp': 'Not posted', 'link': j['url'],
                              'verified': f'live {STAMP}',
                              'fit': f'Auto-swept from the {meta["company"]} board {date.today():%-m.%d.%y} — not yet reviewed for fit.',
                              'edge': 'Set a status to keep it, or leave as reference.',
                              'lane': meta['lane'], 'ranked': None})
        openings.extend(added)

    # 3. write back
    blob = json.dumps(openings, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    h = h[:m.start(1)] + blob + h[m.end(1):]
    HTML.write_text(h, encoding='utf-8')
    SYNC.write_text(json.dumps(openings, indent=0, ensure_ascii=False), encoding='utf-8')
    print(f'\nverified live: {n_live} · closed: {n_closed} · new added: {len(added)} · total now: {len(openings)}')
    for a in added[:20]:
        print(f'  + {a["company"]} — {a["role"]} ({a["loc"]})')
    if len(added) > 20:
        print(f'  … and {len(added) - 20} more')


if __name__ == '__main__':
    main()
