import os
import hmac
import hashlib
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from flask_login import LoginManager, current_user

from models import db, User
from auth import auth_bp, init_oauth
from api import api_bp
from admin import admin_bp

from data.affiliates import affiliates, CATEGORY_LABELS
from data.testimonials import testimonials
from data.programs import programs, CATEGORY_LABELS as PROGRAM_CATEGORY_LABELS
from data.blogs import blogs, CATEGORY_LABELS as BLOG_CATEGORY_LABELS

load_dotenv()

app = Flask(__name__)

# ── Core config ───────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

# Render ships DATABASE_URL as postgres://, SQLAlchemy needs postgresql://
_db_url = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
if _db_url.startswith('postgres://'):
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI']        = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['GOOGLE_CLIENT_ID']     = os.environ.get('GOOGLE_CLIENT_ID', '')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# ── Extensions ────────────────────────────────────────────────────────────────
db.init_app(app)
init_oauth(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    # API routes get 401 JSON; page routes redirect to login
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Login required', 'login_required': True}), 401
    return redirect(url_for('auth.login', next=request.url))


# ── Blueprints ────────────────────────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)

# Create tables on first boot (idempotent) + safe column migrations
with app.app_context():
    db.create_all()
    # Add new columns to existing tables if missing — idempotent on PostgreSQL
    try:
        db.session.execute(db.text(
            "ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS diet_pref VARCHAR(10) DEFAULT 'all'"
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()

# ── Razorpay (optional — graceful degradation if keys not set) ───────────────
RZP_KEY_ID     = os.environ.get('RAZORPAY_KEY_ID', '')
RZP_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
try:
    import razorpay
    rzp_client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET)) if RZP_KEY_ID else None
except Exception:
    rzp_client = None

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}


def get_gallery():
    gallery_dir = os.path.join(app.static_folder, 'images', 'gallery')
    if not os.path.isdir(gallery_dir):
        return []
    return sorted(
        f for f in os.listdir(gallery_dir)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTS
    )[:9]


@app.context_processor
def inject_globals():
    return {
        'rzp_key_id':   RZP_KEY_ID,
        'current_user': current_user,
        'nav_links': [
            ('/',         'Home',     'home'),
            ('/programs', 'Programs', 'programs'),
            ('/blogs',    'Blogs',    'blogs'),
            ('/tools',    'Tools',    'tools'),
            ('/shop',     'Shop',     'shop'),
            ('/collabs',  'Collabs',  'collabs'),
            ('/about',    'About',    'about'),
            ('/contact',  'Contact',  'contact'),
        ],
        'current_year': datetime.now().year,
    }


# ── Page routes ───────────────────────────────────────────────────────────────

@app.route('/')
def home():
    featured = [p for p in affiliates if p['featured']][:4]
    return render_template(
        'index.html',
        featured=featured,
        category_labels=CATEGORY_LABELS,
        gallery=get_gallery(),
        testimonials=testimonials,
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/shop')
def shop():
    return render_template('shop.html', products=affiliates, category_labels=CATEGORY_LABELS)


@app.route('/programs')
def programs_page():
    return render_template('programs.html', programs=programs,
                           category_labels=PROGRAM_CATEGORY_LABELS)


@app.route('/blogs', endpoint='blogs')
def blogs_page():
    return render_template('blogs.html', blogs=blogs,
                           category_labels=BLOG_CATEGORY_LABELS)


@app.route('/blogs/<slug>')
def blog_post(slug):
    from flask import abort
    post = next((b for b in blogs if b.get('slug') == slug), None)
    if not post:
        abort(404)
    return render_template(f'blog_posts/{slug}.html', blog=post)


@app.route('/tools')
def tools():
    return render_template('tools.html')


@app.route('/tdee')
def tdee():
    return render_template('tdee.html')


@app.route('/tracker')
def tracker():
    return render_template('tracker.html')


@app.route('/collabs')
def collabs():
    return render_template('collabs.html')


# ── SEO ───────────────────────────────────────────────────────────────────────
@app.route('/google736474751546943a.html')
def google_verify():
    return Response('google-site-verification: google736474751546943a.html',
                    mimetype='text/html')
SITE_ROOT = 'https://flexfactorx.onrender.com'

@app.route('/robots.txt')
def robots():
    body = f'User-agent: *\nAllow: /\nSitemap: {SITE_ROOT}/sitemap.xml\n'
    return Response(body, mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap():
    static_pages = [
        ('/',          '2026-06-24', 'weekly',  '1.0'),
        ('/about',     '2026-06-24', 'monthly', '0.6'),
        ('/programs',  '2026-06-24', 'monthly', '0.8'),
        ('/blogs',     '2026-06-24', 'weekly',  '0.9'),
        ('/shop',      '2026-06-24', 'monthly', '0.7'),
        ('/tools',     '2026-06-24', 'monthly', '0.8'),
        ('/collabs',   '2026-06-24', 'monthly', '0.5'),
        ('/contact',   '2026-06-24', 'monthly', '0.5'),
    ]
    urls = []
    for path, lastmod, freq, pri in static_pages:
        urls.append(
            f'  <url>\n'
            f'    <loc>{SITE_ROOT}{path}</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <changefreq>{freq}</changefreq>\n'
            f'    <priority>{pri}</priority>\n'
            f'  </url>'
        )
    for post in blogs:
        urls.append(
            f'  <url>\n'
            f'    <loc>{SITE_ROOT}/blogs/{post["slug"]}</loc>\n'
            f'    <lastmod>{post["date_iso"]}</lastmod>\n'
            f'    <changefreq>monthly</changefreq>\n'
            f'    <priority>0.9</priority>\n'
            f'  </url>'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(urls) +
        '\n</urlset>'
    )
    return Response(xml, mimetype='application/xml')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ── Razorpay API ──────────────────────────────────────────────────────────────

@app.route('/api/create-order', methods=['POST'])
def create_order():
    if not rzp_client:
        return jsonify({'error': 'Payments not configured'}), 503

    data   = request.get_json(silent=True) or {}
    amount = data.get('amount')

    if not isinstance(amount, int) or amount < 100:
        return jsonify({'error': 'Amount must be at least 100 paise'}), 400

    try:
        order = rzp_client.order.create({
            'amount':          amount,
            'currency':        'INR',
            'receipt':         f'ffx_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'payment_capture': 1,
        })
        return jsonify({'order_id': order['id'], 'amount': order['amount'], 'currency': order['currency']})
    except Exception:
        return jsonify({'error': 'Failed to create order'}), 500


@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    if not rzp_client:
        return jsonify({'error': 'Payments not configured'}), 503

    data       = request.get_json(silent=True) or {}
    order_id   = data.get('razorpay_order_id', '')
    payment_id = data.get('razorpay_payment_id', '')
    signature  = data.get('razorpay_signature', '')

    if not all([order_id, payment_id, signature]):
        return jsonify({'error': 'Missing fields'}), 400

    expected = hmac.new(
        RZP_KEY_SECRET.encode(),
        f'{order_id}|{payment_id}'.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        return jsonify({'error': 'Invalid signature'}), 400

    return jsonify({'status': 'ok', 'payment_id': payment_id})


if __name__ == '__main__':
    app.run(debug=True)
