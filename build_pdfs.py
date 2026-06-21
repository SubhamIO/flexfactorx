"""
FlexFactorX — PDF generator (ReportLab).
Run: python build_pdfs.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Paths ───────────────────────────────────────────────────────────────────
BASE    = os.path.dirname(__file__)
OUT     = os.path.join(BASE, 'static', 'pdfs')
LOGO    = os.path.join(BASE, 'flexfactorx_logo.PNG')

# ── Colours ──────────────────────────────────────────────────────────────────
BG      = colors.HexColor('#080808')
ACCENT  = colors.HexColor('#FF4D00')
WHITE   = colors.white
DIM     = colors.HexColor('#888888')
FAINT   = colors.HexColor('#444444')
ROW_A   = colors.HexColor('#111111')
ROW_B   = colors.HexColor('#0D0D0D')
HDR_BG  = colors.HexColor('#1A1A1A')

# ── Page geometry ─────────────────────────────────────────────────────────────
W, H    = A4
MARGIN  = 18 * mm
LOGO_W  = 32 * mm
LOGO_H  = LOGO_W * (374 / 468)          # maintain aspect ratio
HEADER_H = LOGO_H + 6 * mm              # header zone height from top
FOOTER_H = 10 * mm

# ── Paragraph styles ─────────────────────────────────────────────────────────
def _s(name, **kw):
    defaults = dict(fontName='Helvetica', fontSize=9, textColor=WHITE,
                    leading=13, spaceAfter=0, spaceBefore=0)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

S = {
    'tag':   _s('tag',  fontName='Helvetica-Bold', fontSize=6.5,
                textColor=ACCENT, leading=9, tracking=3),
    'h1':    _s('h1',   fontName='Helvetica-Bold', fontSize=24,
                textColor=WHITE,  leading=26, spaceBefore=4, spaceAfter=2),
    'h2':    _s('h2',   fontName='Helvetica-Bold', fontSize=11,
                textColor=ACCENT, leading=13, spaceBefore=10, spaceAfter=3),
    'body':  _s('body', fontSize=8.5, textColor=colors.HexColor('#CCCCCC'), leading=12),
    'small': _s('small',fontSize=7.5, textColor=DIM, leading=11),
    'note':  _s('note', fontName='Helvetica-Oblique', fontSize=8,
                textColor=DIM, leading=11, spaceBefore=4),
    'th':    _s('th',   fontName='Helvetica-Bold', fontSize=8,
                textColor=WHITE,  leading=11, alignment=TA_CENTER),
    'td':    _s('td',   fontSize=8, textColor=colors.HexColor('#CCCCCC'),
                leading=11, alignment=TA_LEFT),
    'tdc':   _s('tdc',  fontSize=8, textColor=colors.HexColor('#CCCCCC'),
                leading=11, alignment=TA_CENTER),
    'bullet':_s('bullet',fontSize=8.5, textColor=colors.HexColor('#CCCCCC'),
                leading=12, leftIndent=8),
}


# ── Page template factory ─────────────────────────────────────────────────────
def make_doc(filename, program_label):
    """Returns a BaseDocTemplate with a dark-themed page template."""
    path = os.path.join(OUT, filename)

    def _draw_page(canvas, doc):
        canvas.saveState()

        # Full-page black background
        canvas.setFillColor(BG)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)

        # Logo — top-left, flush with margin
        logo_y = H - MARGIN - LOGO_H
        canvas.drawImage(LOGO, MARGIN, logo_y,
                         width=LOGO_W, height=LOGO_H,
                         preserveAspectRatio=True, mask='auto')

        # Programme label — top-right, vertically centred with logo
        mid_logo = logo_y + LOGO_H / 2
        canvas.setFont('Helvetica-Bold', 7.5)
        canvas.setFillColor(ACCENT)
        canvas.drawRightString(W - MARGIN, mid_logo + 4, 'FLEXFACTORX')
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(DIM)
        canvas.drawRightString(W - MARGIN, mid_logo - 6, program_label.upper())

        # Orange rule below header
        rule_y = H - MARGIN - LOGO_H - 4 * mm
        canvas.setStrokeColor(ACCENT)
        canvas.setLineWidth(0.8)
        canvas.line(MARGIN, rule_y, W - MARGIN, rule_y)

        # Footer rule
        foot_rule_y = MARGIN + FOOTER_H - 1 * mm
        canvas.setStrokeColor(FAINT)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, foot_rule_y, W - MARGIN, foot_rule_y)

        # Footer text
        canvas.setFont('Helvetica', 6.5)
        canvas.setFillColor(FAINT)
        canvas.drawString(MARGIN, MARGIN + 2, 'FLEXFACTORX  •  ' + program_label.upper())
        canvas.drawRightString(W - MARGIN, MARGIN + 2,
                               f'PAGE {doc.page}  •  FLEXFACTORX.IN')

        canvas.restoreState()

    # Content frame — between header and footer
    frame_top    = H - MARGIN - LOGO_H - 8 * mm
    frame_bottom = MARGIN + FOOTER_H + 1 * mm
    frame = Frame(
        MARGIN, frame_bottom,
        W - 2 * MARGIN, frame_top - frame_bottom,
        leftPadding=0, rightPadding=0, topPadding=4, bottomPadding=0,
    )

    doc = BaseDocTemplate(
        path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=program_label, author='FlexFactorX',
    )
    doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=_draw_page)])
    return doc


# ── Component builders ────────────────────────────────────────────────────────
def section_header(title):
    return [
        Spacer(1, 8),
        Paragraph(title, S['h2']),
        HRFlowable(width='100%', thickness=0.4, color=FAINT,
                   spaceAfter=5, spaceBefore=2),
    ]

def ex_table(rows):
    """rows: [(exercise, sets, reps, notes), ...]"""
    avail = W - 2 * MARGIN
    cw = [avail * 0.38, avail * 0.10, avail * 0.14, avail * 0.38]
    data = [[Paragraph(h, S['th']) for h in ('EXERCISE', 'SETS', 'REPS', 'NOTES')]]
    for ex, sets, reps, notes in rows:
        data.append([
            Paragraph(ex,    S['td']),
            Paragraph(sets,  S['tdc']),
            Paragraph(reps,  S['tdc']),
            Paragraph(notes, S['td']),
        ])
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',      (0, 0), (-1, 0),  HDR_BG),
        ('LINEBELOW',       (0, 0), (-1, 0),  1, ACCENT),
        ('ROWBACKGROUNDS',  (0, 1), (-1, -1), [ROW_A, ROW_B]),
        ('GRID',            (0, 0), (-1, -1), 0.25, colors.HexColor('#2A2A2A')),
        ('TOPPADDING',      (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',   (0, 0), (-1, -1), 4),
        ('LEFTPADDING',     (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',    (0, 0), (-1, -1), 5),
        ('VALIGN',          (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return [t, Spacer(1, 6)]

def bullets(title, points):
    out = section_header(title)
    for p in points:
        out.append(Paragraph(f'•  {p}', S['bullet']))
    return out

def generic_table(header_row, data_rows, col_widths):
    avail = W - 2 * MARGIN
    cw = [avail * f for f in col_widths]
    data = [[Paragraph(h, S['th']) for h in header_row]]
    for row in data_rows:
        data.append([Paragraph(str(c), S['tdc'] if i > 0 else S['td'])
                     for i, c in enumerate(row)])
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',      (0, 0), (-1, 0),  HDR_BG),
        ('LINEBELOW',       (0, 0), (-1, 0),  1, ACCENT),
        ('ROWBACKGROUNDS',  (0, 1), (-1, -1), [ROW_A, ROW_B]),
        ('GRID',            (0, 0), (-1, -1), 0.25, colors.HexColor('#2A2A2A')),
        ('TOPPADDING',      (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',   (0, 0), (-1, -1), 4),
        ('LEFTPADDING',     (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',    (0, 0), (-1, -1), 5),
        ('VALIGN',          (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return [t, Spacer(1, 8)]


KEEP_IN_MIND = [
    'Warm up 5–10 min before every session. Cold muscles = injuries.',
    'Never sacrifice form for weight — ego lifting kills progress.',
    'Hydrate: minimum 3 L water per day on training days.',
    'Track macros. Nutrition is 70% of your results.',
]


# ══════════════════════════════════════════════════════════════════════════════
# PDF BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def build_advanced():
    label = 'Advanced — World of FlexFactorX'
    story = []
    story.append(Paragraph('FLEXFACTORX', S['tag']))
    story.append(Paragraph('ADVANCED PROGRAM', S['h1']))
    story.append(Paragraph('Push · Pull · Legs  —  High Volume', S['small']))
    story.append(Spacer(1, 6))

    story += section_header('PUSH DAY  (Chest · Shoulders · Triceps)')
    story += ex_table([
        ('Bench Press',                    '4', '6–8',  'Primary compound — strength focus'),
        ('Incline Dumbbell Press',         '3', '8–10', 'Upper chest emphasis'),
        ('Cable Fly / Pec Deck',           '3', '12–15','Squeeze at peak contraction'),
        ('Seated Shoulder Press (DB/BB)',  '4', '8–10', 'Strict form, no lower-back arch'),
        ('Lateral Raises',                 '4', '15–20','Slow eccentrics, slight lean'),
        ('Cable Lateral Raises',           '3', '15–20','Unilateral, constant tension'),
        ('Rear Delt Fly (Machine/Cable)',  '3', '15–20','Elbows flared, retract scapula'),
        ('Tricep Pushdowns (Rope)',        '3', '12–15','Full extension, lock out'),
        ('Overhead Tricep Extension',      '3', '10–12','Long head stretch at bottom'),
        ('Skull Crushers',                 '3', '10–12','Bar to forehead, controlled'),
        ('Chest Dips',                     '3', 'Failure','Lean forward for chest bias'),
        ('Cable Crossover',                '2', '15',   'Finisher — squeeze hard'),
    ])

    story += section_header('PULL DAY  (Back · Biceps)')
    story += ex_table([
        ('Deadlift',                       '4', '4–6',  'Brace core, neutral spine'),
        ('Barbell Row',                    '4', '6–8',  'Row to waist, chest to pad'),
        ('Lat Pulldown (Wide Grip)',        '3', '10–12','Full stretch at top'),
        ('Seated Cable Row',               '3', '10–12','Drive elbows back hard'),
        ('Single Arm DB Row',              '3', '10–12','Stretch lats, row to hip'),
        ('Straight Arm Pulldown',          '3', '12–15','Lat isolation — constant tension'),
        ('Face Pulls',                     '3', '15–20','External rotation, rear delt'),
        ('Barbell Bicep Curl',             '4', '8–10', 'Full ROM, no swinging'),
        ('Incline Dumbbell Curl',          '3', '10–12','Long head stretch'),
        ('Hammer Curl',                    '3', '10–12','Brachialis + brachioradialis'),
        ('Cable Curl (Rope)',              '3', '12–15','Squeeze at peak'),
        ('Reverse Curl',                   '2', '12–15','Forearm development'),
    ])

    story += section_header('LEGS DAY  (Quads · Hamstrings · Calves)')
    story += ex_table([
        ('Barbell Back Squat',             '4', '6–8',  'Depth below parallel, brace'),
        ('Leg Press',                      '4', '10–12','Full range, shoulder-width feet'),
        ('Romanian Deadlift',              '3', '10–12','Hip hinge — feel the hamstring'),
        ('Leg Curl (Lying/Seated)',         '3', '12–15','Full extension, slow eccentric'),
        ('Leg Extension',                  '3', '15',   'VMO squeeze at top'),
        ('Standing Calf Raise',            '4', '15–20','Full ROM — pause at stretch'),
        ('Seated Calf Raise',              '3', '20',   'Soleus focus, different angle'),
    ])

    story += bullets('KEEP IN MIND', [
        'Rest 2–3 min between compound sets; 60–90 s isolation.',
        'Progressive overload is mandatory — log every single session.',
        'Deload every 6–8 weeks: drop volume/intensity by 40%.',
        'Sleep 7–9 hours. Muscle is built outside the gym.',
    ])
    story += bullets('UNIVERSAL RULES', KEEP_IN_MIND)

    make_doc('Advanced.pdf', label).build(story)
    print('✓ Advanced.pdf')


def build_beginner():
    label = 'Beginner PPL'
    story = []
    story.append(Paragraph('FLEXFACTORX', S['tag']))
    story.append(Paragraph('BEGINNER PPL PLAN', S['h1']))
    story.append(Paragraph('Push · Pull · Legs  —  3 Days / Week', S['small']))
    story.append(Spacer(1, 6))

    story += section_header('PUSH DAY  (Chest · Shoulders · Triceps)')
    story += ex_table([
        ('Bench Press',              '3', '8–10',  'Learn the movement pattern first'),
        ('Overhead Press (BB)',      '3', '8–10',  'Seated or standing, strict form'),
        ('Incline DB Press',         '3', '10–12', 'Control the descent each rep'),
        ('Lateral Raises',           '3', '12–15', 'Light weight, full ROM'),
        ('Tricep Pushdown (Rope)',    '3', '12–15', 'Full extension each rep'),
    ])

    story += section_header('PULL DAY  (Back · Biceps)')
    story += ex_table([
        ('Lat Pulldown',             '3', '10–12', 'Pull to upper chest, full stretch'),
        ('Seated Cable Row',         '3', '10–12', 'Drive elbows back, squeeze'),
        ('Dumbbell Row',             '3', '10–12', 'One side at a time, controlled'),
        ('Face Pulls',               '3', '15',    'Rear delt + rotator cuff health'),
        ('Barbell Curl',             '3', '10–12', 'No swinging, full ROM'),
    ])

    story += section_header('LEGS DAY  (Quads · Hamstrings · Calves)')
    story += ex_table([
        ('Goblet Squat / Back Squat','3', '10–12', 'Depth first — then add load'),
        ('Romanian Deadlift',        '3', '10–12', 'Feel the hamstring stretch'),
        ('Leg Press',                '3', '12',    'Full range of motion'),
        ('Leg Curl (Machine)',        '3', '12–15', 'Slow eccentric, full stretch'),
        ('Standing Calf Raise',      '3', '15–20', 'Pause at bottom for stretch'),
    ])

    story += bullets('KEEP IN MIND', [
        'Rest 90 s compounds, 60 s isolation. Shorter rest = more metabolic stress.',
        'Add weight only when you complete all reps with clean form.',
        'Run this for 6–12 weeks before increasing frequency or switching.',
        'Focus on the mind-muscle connection — feel the target muscle work.',
    ])
    story += bullets('UNIVERSAL RULES', KEEP_IN_MIND)

    make_doc('beginnerppl.pdf', label).build(story)
    print('✓ beginnerppl.pdf')


def build_aesthetic():
    label = 'Aesthetic PPL'
    story = []
    story.append(Paragraph('FLEXFACTORX', S['tag']))
    story.append(Paragraph('AESTHETIC PPL PLAN', S['h1']))
    story.append(Paragraph('Push · Pull · Legs  —  Physique Focus', S['small']))
    story.append(Spacer(1, 6))

    story += section_header('PUSH DAY  (Chest · Shoulders · Triceps)')
    story += ex_table([
        ('Incline Bench Press',           '4', '8–10',  'Upper chest priority for fullness'),
        ('Cable Fly (Low-to-High)',        '3', '12–15', 'Inner chest sweep, squeeze peak'),
        ('Seated DB Shoulder Press',      '4', '10–12', 'Full ROM, controlled tempo'),
        ('Lateral Raise + Rear Delt SS',  '3', '15/15', 'Superset — 3D delt roundness'),
        ('Skull Crushers',                '3', '10–12', 'Long head stretch at bottom'),
        ('Cable Pushdown',                '3', '12–15', 'Constant tension, rope attachment'),
        ('Cable Crossover Finisher',      '2', '15',    'Arms parallel to floor, squeeze'),
    ])

    story += section_header('PULL DAY  (Back · Biceps · Rear Delt)')
    story += ex_table([
        ('Wide Grip Pull-ups / Pulldown', '4', '8–10',  'V-taper width builder'),
        ('Chest Supported Row',           '3', '10–12', 'Isolate back, zero momentum'),
        ('Cable Seated Row (Close Grip)', '3', '10–12', 'Mid-back thickness'),
        ('Straight Arm Pulldown',         '3', '12–15', 'Lat isolation, constant tension'),
        ('Incline DB Curl',               '3', '10–12', 'Long head emphasis, peak'),
        ('Hammer Curl',                   '3', '12',    'Brachialis peak width'),
    ])

    story += section_header('LEGS DAY  (Quads · Hamstrings · Glutes · Calves)')
    story += ex_table([
        ('Leg Press (High & Wide)',       '4', '10–12', 'Glute + quad sweep'),
        ('Bulgarian Split Squat',         '3', '10/side','Unilateral balance + strength'),
        ('Romanian Deadlift',             '4', '10–12', 'Hamstring + glute stretch'),
        ('Leg Extension',                 '3', '15',    'VMO focus, squeeze at top'),
        ('Lying Leg Curl',                '3', '12–15', 'Slow eccentric, full stretch'),
        ('Seated Calf Raise',             '4', '20',    'Soleus — pause at bottom'),
    ])

    story += bullets('KEEP IN MIND', [
        'Prioritise the pump — slow eccentrics (3–4 s down) on isolation work.',
        'Symmetry is built by identifying and hammering weak points.',
        'Cardio: 2–3 x 20–30 min LISS sessions per week to stay lean.',
        'Posing practice: 5 min/day teaches you to flex and control muscles.',
        'Slight calorie surplus (200–300 kcal over TDEE) for lean bulking.',
    ])
    story += bullets('UNIVERSAL RULES', KEEP_IN_MIND)

    make_doc('Aesthetic.pdf', label).build(story)
    print('✓ Aesthetic.pdf')


def build_bro_split():
    label = 'Bro Split Variation'
    story = []
    story.append(Paragraph('FLEXFACTORX', S['tag']))
    story.append(Paragraph('BRO SPLIT VARIATION', S['h1']))
    story.append(Paragraph('5-Day Split  —  Classic Bodybuilding', S['small']))
    story.append(Spacer(1, 6))

    story += section_header('DAY 1  —  CHEST')
    story += ex_table([
        ('Bench Press (BB)',        '4', '6–8',   'Primary strength movement'),
        ('Incline DB Press',        '3', '8–10',  'Upper chest sweep'),
        ('Cable Fly',               '3', '12–15', 'Isolation, constant tension'),
        ('Chest Dips',              '3', 'Failure','Lean forward for chest bias'),
        ('Push-ups (Weighted)',     '3', 'Failure','Finisher — flush the muscle'),
    ])

    story += section_header('DAY 2  —  BACK')
    story += ex_table([
        ('Deadlift',                '4', '5',     'Max effort, perfect form'),
        ('Pull-ups',                '3', '8–10',  'Full hang to chin over bar'),
        ('Barbell Row',             '4', '8–10',  'Row to waist, not chest'),
        ('Lat Pulldown',            '3', '10–12', 'Wide grip, slight back lean'),
        ('Cable Row (Close Grip)',  '3', '10–12', 'Squeeze shoulder blades'),
    ])

    story += section_header('DAY 3  —  SHOULDERS')
    story += ex_table([
        ('Overhead Press (BB)',     '4', '6–8',   'Standing or seated strict'),
        ('DB Lateral Raise',        '4', '15–20', 'Slight lean, slow eccentrics'),
        ('Rear Delt Fly',           '3', '15–20', 'Face down incline bench'),
        ('Front Raise',             '2', '12',    'Alternate arms, controlled'),
        ('Shrugs',                  '3', '15',    'Slow, full ROM, hold at top'),
    ])

    story += section_header('DAY 4  —  ARMS')
    story += ex_table([
        ('Barbell Curl',            '4', '8–10',  'Full ROM, no swing'),
        ('Incline DB Curl',         '3', '10–12', 'Long head stretch'),
        ('Hammer Curl',             '3', '12',    'Brachialis thickness'),
        ('Skull Crushers',          '4', '10–12', 'Bar to forehead, long head'),
        ('Tricep Pushdown',         '3', '12–15', 'Rope, full extension'),
        ('Overhead Tricep Ext',     '3', '12',    'Single DB, long head focus'),
    ])

    story += section_header('DAY 5  —  LEGS')
    story += ex_table([
        ('Barbell Squat',           '4', '6–8',   'Depth below parallel'),
        ('Leg Press',               '4', '10–12', 'Shoulder-width, full ROM'),
        ('Romanian Deadlift',       '3', '10–12', 'Hamstring hinge — slow'),
        ('Leg Curl',                '3', '12–15', 'Slow eccentric, full stretch'),
        ('Leg Extension',           '3', '15',    'VMO squeeze at top'),
        ('Standing Calf Raise',     '4', '20',    'Pause at full stretch'),
    ])

    story += bullets('KEEP IN MIND', [
        'Rest 2–3 min compounds, 60–90 s isolation.',
        'Bro split works — high frequency diet and sleep seal the deal.',
        'Rotate exercises every 6–8 weeks to prevent adaptation.',
        'Priority principle: train your weakest area first while energy is highest.',
    ])
    story += bullets('UNIVERSAL RULES', KEEP_IN_MIND)

    make_doc('Bro_Split.pdf', label).build(story)
    print('✓ Bro_Split.pdf')


def build_fat_loss():
    label = 'Fat Loss PPL'
    story = []
    story.append(Paragraph('FLEXFACTORX', S['tag']))
    story.append(Paragraph('FAT LOSS PPL PLAN', S['h1']))
    story.append(Paragraph('Push · Pull · Legs  —  Cut Phase', S['small']))
    story.append(Spacer(1, 6))

    story += section_header('PUSH DAY')
    story += ex_table([
        ('Bench Press',              '4', '10–12', 'Moderate weight, shorter rest'),
        ('Incline DB Press',         '3', '12–15', 'Keep tension on chest'),
        ('Lateral Raise',            '4', '15–20', 'Light, controlled, metabolic'),
        ('Tricep Pushdown',          '3', '15',    'Superset option with push-ups'),
        ('Push-ups',                 '3', 'Failure','Bodyweight finisher'),
    ])

    story += section_header('PULL DAY')
    story += ex_table([
        ('Pull-ups / Lat Pulldown',  '4', '10–12', 'Full stretch, no kipping'),
        ('Cable Row',                '3', '12–15', 'Slow eccentrics, squeeze peak'),
        ('Face Pulls',               '3', '20',    'High rep — shoulder health'),
        ('Barbell Curl',             '3', '12–15', 'Control the negative'),
        ('Hammer Curl',              '3', '12–15', 'Superset with barbell curl'),
    ])

    story += section_header('LEGS DAY')
    story += ex_table([
        ('Goblet Squat / Leg Press', '4', '15',    'High rep, metabolic burn'),
        ('Romanian Deadlift',        '3', '12–15', 'Feel the stretch — slow'),
        ('Walking Lunges',           '3', '20/leg','Glute + quad + cardio effect'),
        ('Leg Curl',                 '3', '15',    'Slow negative, full stretch'),
        ('Calf Raise',               '3', '25',    'High rep, burn it out'),
    ])

    story += bullets('KEEP IN MIND', [
        'Rest 45–60 s between sets to keep heart rate elevated.',
        'Add 15–20 min LISS cardio after training or on rest days.',
        'Caloric deficit: 300–500 kcal below TDEE — no more.',
        'Protein target: 2.2 g per kg of bodyweight to protect muscle.',
        'Do NOT drop intensity — lower calories, not training performance.',
    ])
    story += bullets('UNIVERSAL RULES', KEEP_IN_MIND)

    make_doc('Fat_loss.pdf', label).build(story)
    print('✓ Fat_loss.pdf')


def build_strength():
    label = 'Strength PPL'
    story = []
    story.append(Paragraph('FLEXFACTORX', S['tag']))
    story.append(Paragraph('STRENGTH PPL PLAN', S['h1']))
    story.append(Paragraph('Push · Pull · Legs  —  Powerbuilding', S['small']))
    story.append(Spacer(1, 6))

    story += section_header('PUSH DAY  (Strength Focus)')
    story += ex_table([
        ('Bench Press',              '5', '3–5',   'Work to top set — linear progression'),
        ('Overhead Press (BB)',      '4', '5',      'Standing strict — no leg drive'),
        ('Close Grip Bench Press',   '3', '8',      'Tricep strength for bench lockout'),
        ('Weighted Dips',            '3', '8–10',  'Heavy — chest + tricep'),
    ])

    story += section_header('PULL DAY  (Strength Focus)')
    story += ex_table([
        ('Conventional Deadlift',    '5', '3–5',   'Max tension — brace throughout'),
        ('Pendlay Row',              '4', '5',      'Explosive pull, reset each rep'),
        ('Weighted Pull-ups',        '3', '6–8',   'Add load when sets feel easy'),
        ('Barbell Curl',             '3', '8',      'Supports elbow flexion for pulls'),
        ('Hammer Curl',              '3', '8',      'Brachialis + forearm strength'),
    ])

    story += section_header('LEGS DAY  (Strength Focus)')
    story += ex_table([
        ('Barbell Back Squat',       '5', '3–5',   'Primary leg strength builder'),
        ('Front Squat / Pause Squat','3', '5',      'Positional strength, quad dominance'),
        ('Romanian Deadlift',        '4', '8',      'Hamstring strength for deadlift'),
        ('Leg Press',                '3', '10',     'Volume for quad development'),
        ('Standing Calf Raise',      '4', '10–12', 'Progressive load, slow reps'),
    ])

    story += bullets('KEEP IN MIND', [
        'Rest 3–5 min between heavy compound sets — CNS recovery is real.',
        'Track estimated 1RM every 6 weeks to measure actual progress.',
        'Linear progression: +2.5 kg upper body, +5 kg lower body each week.',
        'Use a belt for sets above 85% 1RM — a tool, not a crutch.',
        'Mobility work non-negotiable: hips, thoracic spine, ankles.',
    ])
    story += bullets('UNIVERSAL RULES', KEEP_IN_MIND)

    make_doc('Strength.pdf', label).build(story)
    print('✓ Strength.pdf')


def build_pocket_diet():
    label = 'Pocket Diet — World of FlexFactorX'
    story = []
    story.append(Paragraph('FLEXFACTORX', S['tag']))
    story.append(Paragraph('POCKET DIET', S['h1']))
    story.append(Paragraph('Complete Nutrition System  —  World of FlexFactorX', S['small']))
    story.append(Spacer(1, 10))

    # Goal Modifications
    story += section_header('GOAL MODIFICATIONS')
    story += generic_table(
        ['GOAL', 'CALORIES', 'PROTEIN', 'CARBS', 'FATS'],
        [
            ('Fat Loss',             '–300 to –500 kcal', '2.2–2.5 g/kg', 'Moderate', 'Moderate'),
            ('Lean Bulk',            '+200 to +300 kcal', '1.8–2.2 g/kg', 'High',     'Moderate'),
            ('Maintenance / Recomp', 'TDEE',              '2.0 g/kg',     'Moderate', 'Moderate'),
            ('Strength Peaking',     '+100 to +200 kcal', '2.0–2.2 g/kg', 'High',     'Low–Mod'),
        ],
        [0.28, 0.22, 0.18, 0.16, 0.16],
    )

    # Macro Sources
    story += section_header('MACRO SOURCES')
    avail = W - 2 * MARGIN
    macro_data = [
        [Paragraph(h, S['th']) for h in ('PROTEIN SOURCES', 'CARB SOURCES', 'FAT SOURCES')],
    ]
    cols = [
        ['Chicken breast', 'Eggs / Egg whites', 'Paneer (low-fat)', 'Greek yoghurt',
         'Tuna / Salmon', 'Whey protein', 'Lentils / Dal', 'Tofu'],
        ['White / Brown rice', 'Oats', 'Sweet potato', 'Whole wheat roti',
         'Banana', 'Fruits', 'White bread (pre-WO)', 'Poha / Upma'],
        ['Almonds / Walnuts', 'Peanut butter', 'Ghee (limited)', 'Avocado',
         'Olive oil', 'Coconut oil', 'Egg yolk', 'Flax seeds'],
    ]
    for i in range(8):
        macro_data.append([Paragraph(c[i], S['td']) for c in cols])
    mt = Table(macro_data, colWidths=[avail / 3] * 3, repeatRows=1)
    mt.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0),  HDR_BG),
        ('LINEBELOW',      (0, 0), (-1, 0),  1, ACCENT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [ROW_A, ROW_B]),
        ('GRID',           (0, 0), (-1, -1), 0.25, colors.HexColor('#2A2A2A')),
        ('TOPPADDING',     (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 3),
        ('LEFTPADDING',    (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 5),
    ]))
    story += [mt, Spacer(1, 8)]

    # 4-Week Timeline
    story += section_header('4-WEEK PROGRESSION TIMELINE')
    story += generic_table(
        ['WEEK', 'FOCUS'],
        [
            ('Week 1', 'Establish baseline. Track every meal. Hit protein target above all else.'),
            ('Week 2', 'Tighten calorie window. Assess hunger, energy, and scale trend.'),
            ('Week 3', 'Adjust: if scale unchanged, reduce by 100–150 kcal further.'),
            ('Week 4', 'Review progress photos + 7-day scale average. Plan next phase.'),
        ],
        [0.12, 0.88],
    )

    # Food Exchange Master List
    story += section_header('FOOD EXCHANGE MASTER LIST')
    story.append(Paragraph('Per 100 g  —  use to swap equivalent protein / carb / fat sources', S['small']))
    story.append(Spacer(1, 4))

    food_rows = [
        # Proteins
        ('Chicken breast (cooked)',  '165', '31',  '0',    '3.6'),
        ('Egg whole',                '155', '13',  '1.1',  '11'),
        ('Egg white',                '52',  '11',  '0.7',  '0.2'),
        ('Paneer (low-fat)',         '265', '18',  '3.4',  '20'),
        ('Greek yoghurt',            '59',  '10',  '3.6',  '0.4'),
        ('Tuna (canned, water)',     '84',  '20',  '0',    '0.5'),
        ('Whey protein (30g scoop)', '120', '24',  '3',    '2'),
        ('Tofu (firm)',              '76',  '8',   '1.9',  '4.8'),
        ('Lentils (cooked)',         '116', '9',   '20',   '0.4'),
        # Carbs
        ('White rice (cooked)',      '130', '2.7', '28',   '0.3'),
        ('Brown rice (cooked)',      '111', '2.6', '23',   '0.9'),
        ('Oats (dry)',               '389', '17',  '66',   '7'),
        ('Sweet potato (cooked)',    '86',  '1.6', '20',   '0.1'),
        ('Whole wheat roti (1 pc)',  '70',  '3',   '14',   '1'),
        ('Banana',                   '89',  '1.1', '23',   '0.3'),
        ('White bread (2 slices)',   '132', '4.4', '25',   '1.8'),
        ('Poha (cooked)',            '110', '2',   '24',   '0.3'),
        # Fats
        ('Almonds',                  '579', '21',  '22',   '50'),
        ('Walnuts',                  '654', '15',  '14',   '65'),
        ('Peanut butter',            '588', '25',  '20',   '50'),
        ('Ghee',                     '900', '0',   '0',    '100'),
        ('Olive oil',                '884', '0',   '0',    '100'),
        ('Avocado',                  '160', '2',   '9',    '15'),
        ('Flax seeds',               '534', '18',  '29',   '42'),
        ('Egg yolk',                 '322', '16',  '3.6',  '27'),
    ]
    fw = W - 2 * MARGIN
    food_data = [[Paragraph(h, S['th']) for h in ('FOOD', 'CAL', 'P (g)', 'C (g)', 'F (g)')]]
    for row in food_rows:
        food_data.append([
            Paragraph(row[0], S['td']),
            Paragraph(row[1], S['tdc']),
            Paragraph(row[2], S['tdc']),
            Paragraph(row[3], S['tdc']),
            Paragraph(row[4], S['tdc']),
        ])
    ft = Table(food_data, colWidths=[fw * 0.40, fw * 0.15, fw * 0.15, fw * 0.15, fw * 0.15],
               repeatRows=1)
    ft.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0),  HDR_BG),
        ('LINEBELOW',      (0, 0), (-1, 0),  1, ACCENT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [ROW_A, ROW_B]),
        ('GRID',           (0, 0), (-1, -1), 0.25, colors.HexColor('#2A2A2A')),
        ('TOPPADDING',     (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 3),
        ('LEFTPADDING',    (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 5),
    ]))
    story += [ft, Spacer(1, 10)]

    # Tracking Tools
    story += section_header('TRACKING TOOLS')
    story += generic_table(
        ['TOOL', 'USE CASE', 'RECOMMENDED APP / METHOD'],
        [
            ('Calorie tracker',   'Log daily food intake',        'MyFitnessPal / Cronometer'),
            ('Kitchen scale',     'Accurate portion sizes',       'Any digital scale (±1 g)'),
            ('Body weight scale', 'Track weekly average',         'Weigh daily — average 7 days'),
            ('Progress photos',  'Visual change over time',      'Every 2 weeks, same lighting'),
            ('Training log',     'Ensure progressive overload',  'Notebook or Strong app'),
        ],
        [0.22, 0.35, 0.43],
    )

    story.append(Paragraph(
        'Koi bhi plan tab kaam karta hai jab aap use consistently follow karo. '
        'Results patience maangti hai — ek din miss karo toh ghabraao mat, '
        'bas agli meal se wapas track par aao.',
        S['note'],
    ))

    make_doc('Pocket_Diet.pdf', label).build(story)
    print('✓ Pocket_Diet.pdf')


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    build_advanced()
    build_beginner()
    build_aesthetic()
    build_bro_split()
    build_fat_loss()
    build_strength()
    build_pocket_diet()
    print('\nAll 7 PDFs saved to static/pdfs/')
