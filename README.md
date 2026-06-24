# FLEXFACTORX

> Science-backed fitness training, trusted supplement picks, and free tools — built for people who are serious about results.

**Live site → [flexfactorx.onrender.com](https://flexfactorx.onrender.com)**
&nbsp;·&nbsp;
**Instagram → [@flexfactorx](https://instagram.com/flexfactorx)**

---

## What is FlexFactorX?

FlexFactorX is a fitness content and tools platform built by an athlete, for athletes. No fluff. No generic advice. Just the stuff that actually works — science-backed programs, honest supplement recommendations, and free calculators that most apps charge a subscription for.

The stack is intentionally lean: Flask backend, Tailwind CSS, PostgreSQL for user data, and Google OAuth for frictionless sign-in. Fast, functional, and built to scale.

---

## Features

### Free Fitness Tools
The most feature-complete free tools in the Indian fitness space.

**TDEE Calculator**
- Mifflin-St Jeor BMR formula + activity multipliers
- Full macro blueprint (protein, carbs, fat) with food equivalents in rotis, rice, eggs
- Goal timeline — how long to reach your target weight at this pace
- 7 deep insights most apps charge for: metabolic adaptation, recomp limits, NEAT leverage, and more
- Pace warnings when cut/bulk rate exceeds safe thresholds

**Daily Calorie + Workout Tracker**
- Log food across 4 meals — 110+ Indian foods (ghee, dal, roti, biryani, paneer, all of it)
- Log workouts — 22 cardio + 21 strength exercises with MET-based calorie burn
- Net calorie balance: food eaten − workout burned = real daily number
- 7-day weekly chart with trend analysis
- Smart insight that tells you exactly what to do next
- **Cloud sync** when signed in — data persists across all your devices

### Training Programs
Seven programs covering every goal and experience level — free PDF downloads.

| # | Program | Level | Frequency |
|---|---|---|---|
| 01 | Advanced PPL | Advanced | 6 days/week |
| 02 | Beginner PPL | Beginner | 3 days/week |
| 03 | Aesthetic PPL | Intermediate | 3 days/week |
| 04 | Bro Split | Intermediate | 5 days/week |
| 05 | Fat Loss PPL | All Levels | 3 days/week |
| 06 | Strength PPL | Intermediate | 3 days/week |
| 07 | Pocket Diet | All Levels | Reference guide |

### Shop — Trusted Supplements
Every product personally used and vetted. Affiliate links help keep the content free.

| Product | Brand | Link |
|---|---|---|
| MB-Vite Multivitamin + Omega 3 Combo | MuscleBlaze | [Buy on Amazon](https://amzn.to/4xN0Ggj) |
| Pure Micronised Creatine Monohydrate | Wellcore | [Buy on Amazon](https://link.amazon/B01GkcDbh) |
| Fermented Yeast Protein — Swiss Chocolate | Bolt | [Buy on Amazon](https://link.amazon/B0dxSC9vk) |
| Beetroot Extract 8000mg | Carbamide Forte | [Buy on Amazon](https://link.amazon/B042d5Keb) |
| Shilajit Gold 750mg Effervescent | Carbamide Forte | [Buy on Amazon](https://link.amazon/B05j4dz9j) |
| High Protein Peanut Butter — Dark Chocolate | Pintola | [Buy on Amazon](https://link.amazon/B0h6EcrB9) |
| High Protein Oats — Dark Chocolate 1kg | Pintola | [Buy on Amazon](https://link.amazon/B0fHc1JA7) |
| Smart Caffeine (Caffeine + L-Theanine) | Smart Caffeine | [Buy here](https://getsmartcaffeine.com/?ref=lnmzvuuy) — use code **25OFFCAFFEINE** |
| Pull Up Bar — Doorway Chin Up Bar | Boldfit | [Buy on Amazon](https://link.amazon/B06hj9FCU) |

---

## Support the Work

If FlexFactorX has helped you — a program, a tool, an insight that actually made a difference — consider supporting. It keeps the content free and the site running.

**[Support FlexFactorX →](https://flexfactorx.onrender.com/programs)**

Every rupee goes directly into more content, better tools, and zero-paywall programs.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python · Flask |
| Database | PostgreSQL (Render managed) |
| Auth | Google OAuth 2.0 · Flask-Login · Authlib |
| ORM | Flask-SQLAlchemy · Flask-Migrate |
| Frontend | Jinja2 · Tailwind CSS (CDN) |
| Fonts | Bebas Neue · Inter |
| Payments | Razorpay |
| Deploy | Render (web service + PostgreSQL) |
| Forms | Formspree |

---

## Project Structure

```
flexfactorx/
├── app.py              # Flask app factory, routes, Razorpay integration
├── models.py           # SQLAlchemy models — users, food logs, workouts, TDEE snapshots
├── auth.py             # Google OAuth blueprint
├── api.py              # REST API — tracker CRUD, weekly summary, analytics
├── admin.py            # Admin dashboard blueprint (access-controlled)
├── data/
│   ├── affiliates.py   # Affiliate product catalogue
│   ├── programs.py     # Training program metadata
│   └── testimonials.py # Social proof data
├── templates/
│   ├── base.html       # Layout, navbar, footer
│   ├── index.html      # Homepage
│   ├── tools.html      # TDEE calculator + tracker (combined)
│   ├── programs.html   # Training programs
│   ├── shop.html       # Affiliate shop
│   ├── login.html      # Google sign-in
│   ├── admin.html      # Admin dashboard
│   └── admin_user.html # Per-user detail view
├── static/
│   ├── css/main.css
│   ├── js/main.js
│   └── images/
├── requirements.txt
└── render.yaml
```

---

## Database Schema

```
users               → Google profile, created_at, last_login
user_settings       → calorie goal, macros, body weight (one per user)
food_logs           → per-meal food entries with full macro breakdown
workout_logs        → exercise entries with MET-based calorie burn
weight_history      → daily body weight check-ins
tdee_snapshots      → every TDEE calculation (analytics + goal tracking)
```

---

## Local Development

```bash
# Clone
git clone https://github.com/SubhamIO/flexfactorx.git
cd flexfactorx

# Virtual environment
python -m venv venv && source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Environment variables — create a .env file:
# SECRET_KEY=your-secret-key
# DATABASE_URL=postgresql://... (or sqlite:///dev.db for local)
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret
# RAZORPAY_KEY_ID=your-razorpay-key
# RAZORPAY_KEY_SECRET=your-razorpay-secret
# ADMIN_EMAIL=your-email@gmail.com

# Run
flask run
```

App runs at `http://localhost:5000`.
Tables are created automatically on first boot via `db.create_all()`.

---

## Deployment (Render)

1. Push to GitHub
2. Create a new **Web Service** on Render — connect the repo
3. Add a **PostgreSQL** database — `DATABASE_URL` is auto-injected
4. Add environment variables: `SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `ADMIN_EMAIL`
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`

Google OAuth setup: add `https://your-app.onrender.com/auth/callback` as an authorized redirect URI in Google Cloud Console.

---

## Admin Dashboard

Accessible at `/admin` — your Google email must match `ADMIN_EMAIL` in the environment.

Shows:
- Platform stats (users, active users, food entries, workouts, TDEE calculations)
- 7-day signup trend + 14-day daily active trackers chart
- Top 10 most logged foods and exercises across all users
- Full user table with days tracked, total calories, last log date
- Per-user detail: current goals, TDEE history, weight trend, 30-day daily log

---

## Affiliate Disclosure

Some links on this site are affiliate links. A small commission may be earned at no extra cost to you. Only products that are personally used and trusted are recommended.

---

## License

Content and programs © FlexFactorX. All rights reserved.
Code available for reference — not licensed for reuse or redistribution.
