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


# ══════════════════════════════════════════════════════════════════════════════
# 9 WAYS TO SLEEP BETTER — Fix Your Sleep, Naturally
# ══════════════════════════════════════════════════════════════════════════════
def build_sleep_better():
    label = '9 Ways to Sleep Better — World of FlexFactorX'
    story = []

    # ── Title block ──
    story.append(Paragraph('FLEXFACTORX  •  RECOVERY', S['tag']))
    story.append(Paragraph('9 WAYS TO SLEEP BETTER', S['h1']))
    story.append(Paragraph('Fix Your Sleep, Naturally', S['small']))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width='100%', thickness=0.4, color=FAINT,
                            spaceAfter=8, spaceBefore=4))

    # ── Intro ──
    story += [Paragraph(
        'Your sleep shapes everything — your mood, your metabolism, your recovery, and how '
        'much muscle you actually keep from all those hard sessions. Yet most people grind '
        'through restless nights and groggy mornings, assuming that’s just how it is. It isn’t. '
        'You don’t need prescriptions or expensive gadgets to fix your sleep. These nine '
        'science-backed strategies work with your body’s natural rhythms — this is the '
        'FlexFactorX playbook for reclaiming deep, restorative sleep.',
        S['lead'],
    )]

    # ── Circadian rhythm primer ──
    story += h2('FIRST — UNDERSTAND YOUR BODY CLOCK')
    story += p(
        'Your circadian rhythm is your internal 24-hour clock. It decides when you feel alert '
        'and when you wind down, mostly by responding to light and darkness and releasing '
        'hormones like melatonin at night. When that rhythm gets disrupted — irregular schedules, '
        'late screens, poor light exposure — your entire sleep architecture falls apart.'
    )
    story += p(
        'The warning signs: trouble falling asleep, waking through the night, morning grogginess '
        'despite enough hours in bed, and energy crashes during the day. Fix the rhythm and you '
        'fix the sleep. Here’s how — nine ways, in order of impact.'
    )

    # ── 1 ──
    story += h2('1. GET BRIGHT LIGHT FIRST THING')
    story += p(
        'Light is the single most powerful lever for resetting your clock. Within the first hour '
        'of waking, get 15–30 minutes of bright light. Natural sunlight is best; a 10,000-lux '
        'light therapy lamp works for early risers or darker months. Morning light tells your '
        'brain to ramp up alertness-promoting cortisol now — so melatonin shows up on time tonight.'
    )

    # ── 2 ──
    story += h2('2. KILL THE BLUE LIGHT AT NIGHT')
    story += p(
        'Cut blue light exposure 2–3 hours before bed. Switch on night mode, wear blue-light '
        'blocking glasses, or better yet create a "digital sunset" by stepping away from screens '
        'entirely. Install blackout curtains for complete darkness — even small amounts of light '
        'can suppress melatonin and fragment your sleep.'
    )

    # ── 3 ──
    story += h2('3. KEEP A CONSISTENT SLEEP SCHEDULE')
    story += p(
        'Your body thrives on predictability. Going to bed and waking at the same time every day '
        '— weekends included — reinforces your rhythm more powerfully than any single trick. Need '
        'to shift your schedule? Move it in 15-minute increments every few days; sudden jumps '
        'backfire. Limit weekend sleep-ins to one hour past your usual wake time to avoid "social '
        'jet lag" that wrecks the week ahead.'
    )

    # ── 4 ──
    story += h2('4. ENGINEER A COOL, DARK, QUIET ROOM')
    story += generic_table(
        ['FACTOR', 'TARGET'],
        [
            ('Temperature', 'Keep the room at 60–67°F (15–19°C) — a cool room supports the natural drop in core body temperature that triggers deep sleep.'),
            ('Light',       'Total darkness. Blackout curtains + eye mask. Cover stray LEDs.'),
            ('Sound',       'Earplugs, a fan, or a white-noise machine to mask disruptions.'),
            ('Air',         'Good circulation and clean air — add a purifier if your area is polluted.'),
        ],
        [0.22, 0.78],
    )

    # ── 5 ──
    story += h2('5. BUILD A WIND-DOWN ROUTINE')
    story += p(
        'A structured wind-down tells your brain that sleep is coming. Start 1–2 hours before your '
        'target bedtime and actively do calming things, not just avoid stimulating ones.'
    )
    story += h3('The Digital Sunset')
    story += p(
        'Switch off all screens at least one hour before bed. Device blue light suppresses '
        'melatonin and keeps your brain in an alert, "online" state.'
    )
    story += h3('Relaxation Techniques')
    story += p(
        'Try progressive muscle relaxation — tense and release each muscle group from your toes '
        'up. Pair it with deep breathing like the 4-7-8 technique to switch on your '
        'parasympathetic ("rest and digest") nervous system and prime your body for sleep.'
    )

    # ── 6 ──
    story += h2('6. USE NATURAL SLEEP AIDS & SMART NUTRITION')
    story += p(
        'The right foods and supplements support your body’s own sleep processes without the '
        'hangover of sleeping pills.'
    )
    story += generic_table(
        ['AID', 'HOW TO USE IT'],
        [
            ('Sleep-promoting foods', 'Tart cherry juice (natural melatonin), chamomile tea, tryptophan-rich foods (turkey, warm milk). Finish eating 3+ hours before bed.'),
            ('Melatonin',             '0.5–3 mg, taken ~30 minutes before bed.'),
            ('Magnesium glycinate',   '200–400 mg — relaxes muscles and calms the nervous system.'),
            ('Valerian root',         'A traditional, evidence-supported relaxation aid.'),
            ('Caffeine cut-off',      'No caffeine within 6 hours of bed — its long half-life lingers even when you feel fine.'),
            ('Hydration',             'Plenty of water through the day, taper 2 hours before bed to limit bathroom trips.'),
        ],
        [0.27, 0.73],
    )
    story += p(
        'Note: supplements can interact with medications. Check with a healthcare provider before '
        'starting anything new — especially if you take prescriptions or have a health condition.'
    )

    # ── 7 ──
    story += h2('7. TIME YOUR EXERCISE RIGHT')
    story += p(
        'Regular training is one of the strongest tools for better sleep — it regulates your '
        'rhythm, lowers stress hormones, and builds your drive for deep sleep. But timing matters. '
        'Morning or afternoon workouts are ideal: exercise raises core temperature, and the drop '
        'a few hours later promotes sleepiness. Avoid hard, vigorous sessions within 3 hours of '
        'bed. If you train in the evening, keep it gentle — yoga, stretching, or an easy walk.'
    )

    # ── 8 ──
    story += h2('8. MANAGE STRESS BEFORE IT MANAGES YOU')
    story += p(
        'Stress and anxiety are the biggest enemies of quality sleep. Racing thoughts and physical '
        'tension keep you up for hours or fragment your nights. Build a stress toolkit you can use '
        'both in the day and at bedtime.'
    )
    story += h3('Mindfulness & Meditation')
    story += p(
        'Spend 10–20 minutes on meditation or a guided body scan before bed to quiet mental '
        'chatter and ease into relaxation.'
    )
    story += h3('Journaling')
    story += p(
        'Keep a bedside journal and "brain dump" worries and tomorrow’s tasks. Clearing the mental '
        'clutter signals your brain that it’s safe to let go and rest.'
    )

    # ── 9 ──
    story += h2('9. TRACK PROGRESS & STAY PATIENT')
    story += p(
        'Reset isn’t instant. Most people notice improvements within 1–2 weeks of consistency, '
        'while a full circadian reset can take 4–6 weeks — longer if you’re recovering from chronic '
        'disruption. Track the right metrics: how fast you fall asleep, number of night wakings, '
        'morning energy, and daytime alertness. Feeling refreshed on waking with steady energy all '
        'day is the real win. On night shifts or an irregular schedule? Stay consistent within your '
        'own pattern, use blackout curtains and an eye mask for daytime sleep, and use light therapy '
        'to anchor your rhythm.'
    )

    # ── FAQ ──
    story += h2('FREQUENTLY ASKED QUESTIONS')
    story += faq('How long until my sleep improves?',
                 'Most people see results within 1–2 weeks of consistent effort. A complete reset '
                 'can take 4–6 weeks, especially after chronic sleep disruption.')
    story += faq('Can I combine multiple natural sleep aids?',
                 'Yes — many complement each other. Magnesium and melatonin pair well, as do '
                 'relaxation techniques and a better sleep environment. Start with one or two before '
                 'adding more.')
    story += faq('What if I work night shifts?',
                 'Stay consistent within your own schedule. Use blackout curtains and an eye mask '
                 'for daytime sleep, and light therapy to shift your rhythm to match your shifts.')
    story += faq('How do I know it’s actually working?',
                 'Track how quickly you fall asleep, night wakings, morning energy, and daytime '
                 'alertness. You should feel more refreshed waking up and have steadier energy.')
    story += faq('Are natural sleep methods safe?',
                 'Generally yes, but some supplements interact with medications. Consult a healthcare '
                 'provider before starting new supplements if you take prescriptions or have a '
                 'health condition.')

    # ── Key takeaways ──
    story += h2('KEY TAKEAWAYS')
    story += p(
        'Better sleep isn’t about perfection — it’s about consistency and patience. Start with the '
        'fundamentals: morning light, consistent timing, and a cool, dark room. Then layer in stress '
        'management, smart nutrition, and a calm evening routine as those habits stick.'
    )
    story += p(
        'Quality sleep is an investment in every part of your health and training. These strategies '
        'work with your body, not against it, and the gains compound over time. Prioritise '
        'restorative sleep today — your future self, and your progress, will thank you.'
    )

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width='100%', thickness=0.4, color=FAINT, spaceAfter=6))
    story.append(Paragraph(
        'Educational content only — not medical advice. Consult a qualified professional before '
        'starting any supplement or making major lifestyle changes. © FlexFactorX. All rights reserved.',
        S['note'],
    ))

    make_doc('sleep-better-naturally.pdf', label).build(story)
    print('✓ sleep-better-naturally.pdf')


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    build_creatine_101()
    build_sleep_better()
    print('\nAll blog PDFs saved to static/pdfs/')
