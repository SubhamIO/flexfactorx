import os
from datetime import datetime
from flask import Flask, render_template
from data.affiliates import affiliates, CATEGORY_LABELS
from data.testimonials import testimonials

app = Flask(__name__)

GALLERY_DIR = os.path.join('static', 'images', 'gallery')
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}


def get_gallery():
    if not os.path.isdir(GALLERY_DIR):
        return []
    return sorted(
        f for f in os.listdir(GALLERY_DIR)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTS
    )[:9]


@app.context_processor
def inject_globals():
    return {
        'nav_links': [
            ('/', 'Home', 'home'),
            ('/about', 'About', 'about'),
            ('/shop', 'Shop', 'shop'),
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


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
