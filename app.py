import os
import hmac
import hashlib
import razorpay
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from data.affiliates import affiliates, CATEGORY_LABELS
from data.testimonials import testimonials
from data.programs import programs, CATEGORY_LABELS as PROGRAM_CATEGORY_LABELS

load_dotenv()

app = Flask(__name__)

RZP_KEY_ID     = os.environ['RAZORPAY_KEY_ID']
RZP_KEY_SECRET = os.environ['RAZORPAY_KEY_SECRET']
rzp_client     = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

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
        'rzp_key_id': RZP_KEY_ID,
        'nav_links': [
            ('/', 'Home', 'home'),
            ('/about', 'About', 'about'),
            ('/programs', 'Programs', 'programs'),
            ('/shop', 'Shop', 'shop'),
            ('/tdee', 'Tools', 'tdee'),
            ('/collabs', 'Collabs', 'collabs'),
            ('/contact', 'Contact', 'contact'),
        ],
        'current_year': datetime.now().year,
    }


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


@app.route('/tdee')
def tdee():
    return render_template('tdee.html')


@app.route('/tracker')
def tracker():
    return render_template('tracker.html')


@app.route('/collabs')
def collabs():
    return render_template('collabs.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/api/create-order', methods=['POST'])
def create_order():
    data   = request.get_json(silent=True) or {}
    amount = data.get('amount')

    if not isinstance(amount, int) or amount < 100:
        return jsonify({'error': 'Amount must be at least 100 paise'}), 400

    try:
        order = rzp_client.order.create({
            'amount':   amount,
            'currency': 'INR',
            'receipt':  f'ffx_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'payment_capture': 1,
        })
        return jsonify({
            'order_id': order['id'],
            'amount':   order['amount'],
            'currency': order['currency'],
        })
    except Exception:
        return jsonify({'error': 'Failed to create order'}), 500


@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
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
