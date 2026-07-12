import json, re
from collections import Counter

SP = '/private/tmp/claude-501/-Users-dags/6fcf10ff-db90-4cfe-b1dd-f1fbf02b2987/scratchpad/'

FILES = [
    ('lane_finance', 'Finance'), ('lane_crypto', 'Crypto'), ('lane_corporate', 'Corporate'),
    ('lane_sports', 'Sports/Ents'), ('lane_wildcard', 'Wildcard'),
    ('austin_tech', 'Tech'), ('austin_finance', 'Finance'), ('austin_crypto', 'Crypto'),
    ('london_finance', 'Finance'), ('london_realestate', 'Real Estate'),
    ('london_startupbd', 'Startups'), ('london_startupops', 'Startups'),
    ('london_startups_roles', 'Startups'),
    ('sf_bigtech', 'Tech'), ('sf_finance', 'Finance'), ('sf_startups', 'Startups'),
    ('la_ents', 'Sports/Ents'), ('la_startups', 'Startups'), ('la_roles', 'Wildcard'),
    ('corporate_consulting_roles', 'Corporate'), ('crypto_fintech_roles', 'Crypto'),
    ('sports_ents_roles', 'Sports/Ents'),
]

def city(loc):
    l = (loc or '').lower()
    if 'austin' in l: return 'Austin'
    if 'london' in l: return 'London'
    if 'san francisco' in l or re.search(r'\bsf\b', l) or 'bay area' in l or 'menlo' in l or 'palo alto' in l or 'hayward' in l: return 'SF'
    if 'los angeles' in l or re.search(r'\bla\b', l) or 'beverly hills' in l or 'santa monica' in l or 'glendale' in l or 'calabasas' in l or 'costa mesa' in l or 'long beach' in l or 'culver' in l: return 'LA'
    if 'nyc' in l or 'new york' in l: return 'NYC'
    if 'remote' in l: return 'Remote'
    return 'Other'

seen = {}
bad = []
for fn, lane in FILES:
    try:
        d = json.load(open(SP + fn + '.json'))
    except Exception as e:
        bad.append((fn, str(e))); continue
    if not isinstance(d, list):
        bad.append((fn, type(d).__name__)); continue
    for r in d:
        if not isinstance(r, dict) or not r.get('company') or not r.get('role'):
            continue
        k = (r['company'].strip().lower(), r['role'].strip().lower())
        if k in seen:
            continue
        seen[k] = {
            'company': r['company'].strip(),
            'role': r['role'].strip(),
            'track': r.get('track', ''),
            'loc': r.get('location', ''),
            'city': city(r.get('location', '')),
            'comp': r.get('comp', 'Not posted'),
            'link': r.get('link', ''),
            'verified': r.get('verified', ''),
            'fit': r.get('fit_note', ''),
            'edge': r.get('edge_note', ''),
            'lane': lane,
        }

# cross-ref against tracker rankings
t = json.load(open(SP + 'tracker_data.json'))
tk = {(r['company'].strip().lower(), r['role'].strip().lower()): r['rank'] for r in t['roles']}
n_in = 0
for k, o in seen.items():
    if k in tk:
        o['ranked'] = tk[k]; n_in += 1
    else:
        o['ranked'] = None

print('bad files:', bad)
print('unique openings:', len(seen))
print('tracker roles:', len(t['roles']))
print('openings already ranked:', n_in, '| unranked/new:', len(seen) - n_in)
print('cities:', Counter(o['city'] for o in seen.values()))
print('lanes:', Counter(o['lane'] for o in seen.values()))
print('verified:', Counter(o['verified'] for o in seen.values()))

out = sorted(seen.values(), key=lambda o: (o['company'].lower(), o['role'].lower()))
json.dump(out, open(SP + 'openings_merged.json', 'w'), indent=0)
print('wrote openings_merged.json')
