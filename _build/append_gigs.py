import re, json

F = '/Users/dags/Desktop/Job Search Materials/Portfolio & Tracker/Job Tracker - July 2026.html'
SP = '/private/tmp/claude-501/-Users-dags/6fcf10ff-db90-4cfe-b1dd-f1fbf02b2987/scratchpad/'

G = lambda co, role, comp, link, ver, fit, edge: {
    'company': co, 'role': role, 'track': 'Gig', 'loc': 'Remote', 'city': 'Remote',
    'comp': comp, 'link': link, 'verified': ver, 'fit': fit, 'edge': edge,
    'lane': 'Gigs', 'ranked': None}

GIGS = [
    G('Mercor', 'AI Training · Finance / Generalist', '$50-$200/hr', 'https://work.mercor.com',
      'live July 2026',
      'Financial modeling, market sizing, investment-research eval tasks for AI labs; resume upload + AI interview, weekly pay, own schedule',
      'Best $/hr fit on this list: finance domain rates $50-$180/hr, investment-analyst tasks to $200/hr; Columbia Applied Math + PubKey strategy work is exactly the profile'),
    G('DataAnnotation', 'AI Trainer · Coding & General', '$20-$60/hr', 'https://www.dataannotation.tech',
      'live July 2026',
      'Fastest start on this list: qualification assessment then open task queue; most projects $20-$30/hr',
      'Coding queues pay $40-$60/hr; reliable task supply vs competitors; start here for cash this week'),
    G('Outlier (Scale AI)', 'Math / STEM AI Trainer', '$15-$50/hr', 'https://outlier.ai',
      'live July 2026',
      'Math-specialist queues value the Applied Math degree; RLHF and reasoning-eval tasks',
      'Task supply fluctuates; effective rate drops with unpaid screening time, treat as a second queue not the anchor'),
    G('Surge AI', 'AI Data Trainer', '$35-$95/hr', 'https://www.surgehq.ai',
      'live July 2026',
      'Higher bar, higher pay: coding evaluator $70-$95/hr, RLHF $35-$50/hr, domain expert $80-$140/hr',
      'Selective intake; strong writing sample and STEM credential help clear the screen'),
    G('Pareto', 'AI Trainer', '$35-$60/hr', 'https://pareto.ai',
      'unconfirmed',
      'General AI-trainer roles at $35-$60/hr per third-party reviews; registration + resume, onboarded by email',
      'Rates not published; selective; worth a 10-minute application alongside the others'),
    G('Alignerr (Labelbox)', 'AI Trainer', '$22-$39/hr', 'https://www.alignerr.com',
      'live July 2026',
      'Typical remote AI-trainer band $22-$39/hr; specialist projects advertised higher with credentials',
      'Steady but mid-rate; queue diversification play'),
    G('Handshake AI', 'AI Trainer · Domain Expert', '$22-$150/hr', 'https://joinhandshake.com/ai',
      'unconfirmed',
      'Targets grads and domain experts for AI-lab training work; Masters/PhD tiers $30-$150/hr',
      'CAUTION: May 2026 payment crisis reported, Project HH workers receiving 20-50% of earned pay; skip until resolved'),
    G('GLG', 'Expert Network · Paid Consults', '$150-$300/hr per call', 'https://glginsights.com/become-a-network-member/',
      'live July 2026',
      'Paid 30-60 min phone consults; position as operator-expert on Bitcoin hospitality, crypto sponsorship economics, prediction-market events',
      'Investors doing DD on Kalshi-adjacent and crypto-consumer names pay for operator POV; a few calls/month = real money, pays ~2 weeks after call'),
    G('AlphaSights', 'Expert Network · Paid Consults', '$200-$500/hr per call', 'https://www.alphasights.com/advisors/',
      'live July 2026',
      'Same model as GLG, typically less stingy on rates; early-career experts with niche knowledge land $200+',
      'Set rate high and hold; Bitcoin venue + sponsorship-market niche is rare enough to command it'),
    G('Guidepoint', 'Expert Network · Paid Consults', '$150-$400/hr per call', 'https://www.guidepoint.com/advisors/',
      'live July 2026',
      'Third expert-network signup; same profile pitch, pro-rated by the minute',
      'Stack all three networks; profile setup is one evening of work total'),
    G('Wyzant', 'Math / SAT Tutor', '$25-$80/hr', 'https://www.wyzant.com/apply',
      'live July 2026',
      'Set your own rate; Columbia Applied Math sells itself for calc, stats, SAT/ACT math',
      'SAT/ACT prep runs $50-$80/hr; evening-friendly, zero conflict with the job hunt'),
    G('Upwork', 'Fintech Writing · Data · Landing Pages', '$50-$100/hr niche', 'https://www.upwork.com',
      'live July 2026',
      'Fintech/crypto technical writing pays $50-$100/hr; dashboards and single-file HTML tools are a sellable service',
      'Portfolio at dag0stin0.github.io is ready-made proof; pitch the vibe-coded dashboard work, not generic writing'),
    G('Crypto publications', 'Freelance Crypto Writer', '$0.40-$0.75/word', 'https://makealivingwriting.com/cryptocurrency-jobs-for-writers/',
      'live July 2026',
      'Fintech/crypto is a top-paying writing niche; per-word beats hourly content rates',
      'Bitcoin fluency from PubKey is the differentiator; pitch venue economics, policy, and prediction-market angles you already own'),
]

h = open(F, encoding='utf-8').read()
m = re.search(r'const OPENINGS=(\[.*?\]);\n', h, re.S)
data = json.loads(m.group(1).replace('<\\/', '</'))
data = [o for o in data if o.get('lane') != 'Gigs'] + GIGS  # idempotent
new = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
h = h[:m.start(1)] + new + h[m.end(1):]

old_note = 'NYC / London / SF / LA / Austin &middot; full dataset'
new_note = 'NYC / London / SF / LA / Austin, plus a Gigs lane of quick remote income plays &middot; full dataset'
if old_note in h:
    h = h.replace(old_note, new_note)

open(F, 'w', encoding='utf-8').write(h)

s = h.index('<script>') + 8
e = h.index('</script>')
open(SP + 'check_script.js', 'w', encoding='utf-8').write(h[s:e])
print('openings now:', len(data), '| gigs:', sum(1 for o in data if o['lane'] == 'Gigs'))
