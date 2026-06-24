"""
FlexFactorX — Blog PDF generator (ReportLab).
Reuses the dark-themed page template + styles from build_pdfs.py.
Run: python build_blogs.py
"""
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

from build_pdfs import S, make_doc, section_header, generic_table, ACCENT, WHITE, DIM, FAINT

# ── Extra blog-specific styles ────────────────────────────────────────────────
S['lead'] = ParagraphStyle(
    'lead', fontName='Helvetica-Oblique', fontSize=10,
    textColor=colors.HexColor('#DDDDDD'), leading=15, spaceAfter=6, spaceBefore=2,
)
S['h3'] = ParagraphStyle(
    'h3', fontName='Helvetica-Bold', fontSize=9.5,
    textColor=WHITE, leading=13, spaceBefore=9, spaceAfter=2,
)
S['p'] = ParagraphStyle(
    'p', fontName='Helvetica', fontSize=8.5,
    textColor=colors.HexColor('#CCCCCC'), leading=13, spaceAfter=6,
)
S['q'] = ParagraphStyle(
    'q', fontName='Helvetica-Bold', fontSize=9,
    textColor=ACCENT, leading=13, spaceBefore=8, spaceAfter=2,
)
S['a'] = ParagraphStyle(
    'a', fontName='Helvetica', fontSize=8.5,
    textColor=colors.HexColor('#CCCCCC'), leading=13, spaceAfter=7,
)


def h2(t):
    return section_header(t)


def h3(t):
    return [Paragraph(t, S['h3'])]


def p(t):
    return [Paragraph(t, S['p'])]


def faq(question, answer):
    return [
        Paragraph(question, S['q']),
        Paragraph(answer, S['a']),
    ]


# ══════════════════════════════════════════════════════════════════════════════
# CREATINE 101 — Beginner's Muscle-Building Guide
# ══════════════════════════════════════════════════════════════════════════════
def build_creatine_101():
    label = 'Creatine 101 — World of FlexFactorX'
    story = []

    # ── Title block ──
    story.append(Paragraph('FLEXFACTORX  •  SUPPLEMENTS', S['tag']))
    story.append(Paragraph('CREATINE 101', S['h1']))
    story.append(Paragraph('The Beginner’s Muscle-Building Guide', S['small']))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width='100%', thickness=0.4, color=FAINT,
                            spaceAfter=8, spaceBefore=4))

    # ── Intro ──
    story += [Paragraph(
        'Creatine is the most studied — and most misunderstood — supplement in the gym. '
        'Most beginners get buried under conflicting advice about doses, timing and safety. '
        'The reality is far simpler than the supplement industry wants you to believe. '
        'Creatine works by topping up your muscles’ energy stores so you can train harder, '
        'recover faster and build muscle quicker. This is the FlexFactorX no-nonsense breakdown: '
        'science-backed, practical, and written the way we’d explain it to a training partner on day one.',
        S['lead'],
    )]

    # ── What is creatine ──
    story += h2('WHAT IS CREATINE & WHY BEGINNERS SHOULD CARE')
    story += p(
        'Creatine is a compound your body already makes and stores — mostly in your muscles, '
        'with a small amount in the brain. You produce roughly 1–2 grams a day, and pull in '
        'about another gram from meat and fish. The catch: that natural supply only fills your '
        'muscle stores to around 60–70% of capacity. Supplementing pushes those stores to 100%, '
        'and that last 30–40% is where the strength and performance payoff lives.'
    )
    story += p(
        'For a beginner, creatine is the safest possible entry point into supplements. While most '
        'products promise the world and deliver nothing, creatine delivers measurable, repeatable '
        'results backed by more than a thousand studies. No hype required.'
    )

    story += h3('The Science: How Creatine Fuels Energy')
    story += p(
        'Your muscles run on ATP (adenosine triphosphate) for explosive, high-intensity effort. '
        'When you lift, your ATP tank empties within the first 10–15 seconds of a hard set. Creatine '
        'helps regenerate ATP faster, so you hold power output for longer — that means an extra rep '
        'or two on the sets that actually drive growth.'
    )

    story += h3('Why It Builds Muscle')
    story += p(
        'Creatine grows muscle through several mechanisms at once. It lets you handle more volume '
        'at higher intensity, which increases mechanical tension — the primary driver of hypertrophy. '
        'It also pulls water into the muscle cell, creating a fuller, more anabolic environment that '
        'supports protein synthesis. More work + a better-primed cell = faster gains.'
    )

    story += h3('Why It’s Safe for New Lifters')
    story += p(
        'Unlike stimulant-based pre-workouts, creatine doesn’t hammer your nervous system or leave you '
        'crashing. It works through natural cellular pathways. The International Society of Sports '
        'Nutrition rates it as one of the safest and most effective supplements on the market.'
    )

    # ── Benefits ──
    story += h2('PROVEN BENEFITS FOR MUSCLE & STRENGTH')
    story += p(
        'The benefits of creatine reach far past raw strength. Research consistently shows users gain '
        '5–15% more muscle than identical training without it — and that gap widens as your training '
        'intensity and volume climb.'
    )
    story += generic_table(
        ['BENEFIT', 'WHAT IT MEANS FOR YOU'],
        [
            ('Power Output',   '5–15% more power on high-intensity sets — heavier weights, sooner.'),
            ('Recovery',       'Faster recovery between sets — more quality volume per session.'),
            ('Muscle Mass',    'Typically 2–4 lb of extra lean muscle over 6–12 weeks of training.'),
            ('Training Volume','Hold higher intensity for longer = greater adaptation over time.'),
        ],
        [0.26, 0.74],
    )

    # ── Types ──
    story += h2('BEST CREATINE TYPES: MONOHYDRATE vs. THE REST')
    story += p(
        'The shelves are full of "advanced" creatine forms, but for a beginner the choice is simple. '
        'Prioritise proven effectiveness over marketing. The most expensive option is almost never the best.'
    )
    story += h3('Creatine Monohydrate — The Gold Standard')
    story += p(
        'Over 95% of all creatine research uses monohydrate. It’s the cheapest form, and it delivers '
        'every benefit the science describes. For a beginner, there is zero reason to buy anything else.'
    )
    story += h3('HCl & Other Forms')
    story += p(
        'Creatine HCl claims better solubility and absorption, but head-to-head research against '
        'monohydrate is thin. Other forms like ethyl ester have actually tested worse than monohydrate. '
        'Don’t pay a premium for marketing.'
    )
    story += h3('What to Look For When Buying')
    story += p(
        'Choose a product with third-party testing for purity. The Creapure® seal indicates '
        'pharmaceutical-grade, German-made creatine. Avoid proprietary blends that hide the actual '
        'creatine content, and skip unnecessary additives. Monohydrate usually costs 50–70% less than '
        'alternatives for identical results — put the savings toward quality protein.'
    )

    # ── Dosage ──
    story += h2('HOW TO TAKE CREATINE: DOSAGE GUIDE')
    story += p(
        'Both loading and non-loading protocols work. Your choice comes down to how fast you want '
        'results and your tolerance for higher initial doses. Consistency beats perfect timing every time.'
    )
    story += generic_table(
        ['PROTOCOL', 'DOSE', 'NOTES'],
        [
            ('Loading Phase',  '20–25 g/day, split into 4–5 doses, for 5–7 days',
             'Saturates muscles fast — benefits within a week. Then drop to maintenance.'),
            ('Gradual Start',  '3–5 g/day from the start',
             'Full saturation in 3–4 weeks. Easier on digestion, simplest routine.'),
            ('Maintenance',    '3–5 g/day, ongoing',
             'Keeps stores topped up. Larger lifters lean to the higher end.'),
        ],
        [0.20, 0.34, 0.46],
    )
    story += h3('Timing: When to Take It')
    story += p(
        'Timing matters far less than consistency. Post-workout may carry a slight edge thanks to '
        'increased blood flow and insulin sensitivity — but the real win is taking it at the same time '
        'every single day, training day or not. Saturation is what counts, not the clock.'
    )

    # ── Safety ──
    story += h2('SAFETY & SIDE EFFECTS (MEN & WOMEN)')
    story += p(
        'Most creatine fears come from outdated info or confusion with other supplements. Decades of '
        'research confirm it as one of the safest strength supplements available.'
    )
    story += h3('Myths vs. Facts')
    story += p(
        'Claims about kidney damage, dehydration and cramping persist despite the evidence pointing the '
        'other way. Long-term studies show no adverse effect on kidney function in healthy individuals, '
        'and creatine does not dehydrate you when water intake is adequate.'
    )
    story += h3('Real Side Effects & How to Manage Them')
    story += p(
        'Some users feel mild digestive discomfort during a loading phase — smaller, more frequent doses '
        'taken with meals fix that. An early 1–3 lb scale jump is increased muscle water content, not fat. '
        'That’s the supplement working, not a problem.'
    )
    story += h3('A Note for Women')
    story += p(
        'Women respond just as well as men. The "bulking up" fear is unfounded — creatine builds lean, '
        'functional muscle, not excess mass. Performance gains and safety profile are the same across the board.'
    )
    story += h3('Who Should Be Cautious')
    story += p(
        'Anyone with pre-existing kidney disease should consult a doctor first. Pregnant or breastfeeding '
        'women should avoid supplementation due to limited safety data in those groups.'
    )

    # ── Maximising results ──
    story += h2('MAXIMISING RESULTS: TRAINING & NUTRITION')
    story += p(
        'Creatine supports your training — it doesn’t replace the fundamentals. The magic is in the synergy '
        'between creatine, hard resistance training and adequate protein.'
    )
    story += generic_table(
        ['FACTOR', 'HOW TO OPTIMISE IT'],
        [
            ('Training',  'Compound lifts (squat, deadlift, bench) in the 6–12 rep range where power matters most.'),
            ('Carbs',     'Pair creatine with simple carbs (fruit/dextrose) to boost uptake via insulin.'),
            ('Protein',   'Hit 0.8–1 g per lb of bodyweight to feed the muscle-building creatine amplifies.'),
            ('Hydration', 'Aim for 3–4 L water daily — more in heat or hard training. Prevents cramps, optimises function.'),
        ],
        [0.22, 0.78],
    )
    story += h3('Timeline: When to Expect Results')
    story += p(
        'Increased training capacity shows up within 5–7 days on a loading phase, or 2–3 weeks without. '
        'Visible muscle changes typically arrive after 4–6 weeks of consistent training and supplementation. '
        'Strength gains usually lead the visible changes by a couple of weeks — trust the process.'
    )

    # ── FAQ ──
    story += h2('FREQUENTLY ASKED QUESTIONS')
    story += faq('Should I start creatine as a beginner?',
                 'Yes. It’s one of the safest, most effective supplements available. Starting early '
                 'accelerates strength and muscle gains while you’re still mastering technique.')
    story += faq('Is creatine good for newbie gains?',
                 'Absolutely. It amplifies the rapid progress beginners already experience, letting you '
                 'train harder and recover faster during your first 6–12 months.')
    story += faq('How much should a beginner take?',
                 'Either 3–5 g daily (gradual), or load with 20–25 g/day for 5–7 days then drop to 3–5 g. '
                 'Both reach the same destination; loading just gets there faster.')
    story += faq('Which creatine is best for beginners?',
                 'Monohydrate. Most researched, cheapest, and delivers every proven benefit. Skip the '
                 'expensive alternatives.')
    story += faq('Can women take creatine?',
                 'Yes — women benefit equally. It builds lean muscle and strength without excess bulk.')
    story += faq('Do I need to cycle off creatine?',
                 'No. Long-term use shows no adverse effects, and there’s no "reset" period required.')
    story += faq('Can I skip the loading phase?',
                 'Yes. 3–5 g daily from the start fully saturates muscles in 3–4 weeks with identical '
                 'long-term results.')
    story += faq('What if I miss a day?',
                 'Once your stores are saturated, the odd missed dose barely matters. Levels stay elevated '
                 'for days — just resume your normal dose, no doubling up.')

    # ── Key takeaways ──
    story += h2('KEY TAKEAWAYS')
    story += p(
        'Creatine is the most beginner-friendly supplement in the muscle-building toolkit. Its safety '
        'profile, deep research backing and proven results make it the obvious first supplement to add. '
        'The formula is simple: quality creatine monohydrate, consistent daily intake, paired with smart '
        'training and nutrition.'
    )
    story += p(
        'Remember — supplements enhance the fundamentals, they don’t replace them. Nail progressive '
        'overload, hit your protein, and recover properly. Get those right and creatine multiplies your '
        'results. Start simple, stay consistent, and let the science do the heavy lifting alongside you.'
    )

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width='100%', thickness=0.4, color=FAINT, spaceAfter=6))
    story.append(Paragraph(
        'Educational content only — not medical advice. Consult a qualified professional before '
        'starting any supplement. © FlexFactorX. All rights reserved.',
        S['note'],
    ))

    make_doc('creatine-101.pdf', label).build(story)
    print('✓ creatine-101.pdf')


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    build_creatine_101()
    print('\nAll blog PDFs saved to static/pdfs/')
