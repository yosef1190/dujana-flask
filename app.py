import os
import uuid
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory, render_template

app = Flask(__name__)
app.secret_key = 'dujana-spare-parts-secret-key-2024-xK9mP'
app.permanent_session_lifetime = timedelta(days=7)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
IMAGES_DIR = os.path.join(UPLOADS_DIR, 'images')
PRODUCTS_FILE = os.path.join(UPLOADS_DIR, 'products.txt')
ADMINS_FILE = os.path.join(UPLOADS_DIR, 'admins.txt')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sha256_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ─── DATA FUNCTIONS ────────────────────────────────────────────────────────────

def read_products():
    products = []
    if not os.path.exists(PRODUCTS_FILE):
        return products
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 14:
                products.append({
                    'id': parts[0],
                    'name_en': parts[1],
                    'name_am': parts[2],
                    'price': float(parts[3]) if parts[3] else 0,
                    'category_en': parts[4],
                    'category_am': parts[5],
                    'stock': int(parts[6]) if parts[6] else 0,
                    'desc_en': parts[7],
                    'desc_am': parts[8],
                    'image_path': parts[9],
                    'seller_en': parts[10],
                    'seller_am': parts[11],
                    'phone': parts[12],
                    'created_at': parts[13]
                })
    return products


def write_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        for p in products:
            line = '|'.join([
                str(p.get('id', '')),
                str(p.get('name_en', '')),
                str(p.get('name_am', '')),
                str(p.get('price', 0)),
                str(p.get('category_en', '')),
                str(p.get('category_am', '')),
                str(p.get('stock', 0)),
                str(p.get('desc_en', '')),
                str(p.get('desc_am', '')),
                str(p.get('image_path', '')),
                str(p.get('seller_en', '')),
                str(p.get('seller_am', '')),
                str(p.get('phone', '')),
                str(p.get('created_at', ''))
            ])
            f.write(line + '\n')


def read_admins():
    admins = []
    if not os.path.exists(ADMINS_FILE):
        return admins
    with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 6:
                admins.append({
                    'id': parts[0],
                    'username': parts[1],
                    'password_hash': parts[2],
                    'full_name': parts[3],
                    'role': parts[4],
                    'created_at': parts[5]
                })
    return admins


def write_admins(admins):
    with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
        for a in admins:
            line = '|'.join([
                str(a.get('id', '')),
                str(a.get('username', '')),
                str(a.get('password_hash', '')),
                str(a.get('full_name', '')),
                str(a.get('role', '')),
                str(a.get('created_at', ''))
            ])
            f.write(line + '\n')


def check_admin_login(username, password):
    admins = read_admins()
    hashed = sha256_hash(password)
    for admin in admins:
        if admin['username'] == username and admin['password_hash'] == hashed:
            return admin
    return None


def initialize_files():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    if not os.path.exists(ADMINS_FILE) or os.path.getsize(ADMINS_FILE) == 0:
        default_admin = [{
            'id': str(uuid.uuid4()),
            'username': 'admin',
            'password_hash': sha256_hash('admin123'),
            'full_name': 'Super Admin',
            'role': 'superadmin',
            'created_at': datetime.now().isoformat()
        }]
        write_admins(default_admin)

    if not os.path.exists(PRODUCTS_FILE) or os.path.getsize(PRODUCTS_FILE) == 0:
        sample_products = [
            {
                'id': str(uuid.uuid4()),
                'name_en': 'Brake Disc Set',
                'name_am': 'የብሬክ ዲስክ ስብስብ',
                'price': 2500.00,
                'category_en': 'Brakes',
                'category_am': 'ብሬክ',
                'stock': 15,
                'desc_en': 'High-performance brake disc set compatible with most sedans and SUVs. Ensures smooth and reliable braking.',
                'desc_am': 'ለአብዛኛዎቹ መኪናዎች የሚሰራ ከፍተኛ አፈጻጸም ያለው የብሬክ ዲስክ ስብስብ። ለስላሳ እና አስተማማኝ ብሬኪንግ ያረጋግጣል።',
                'image_path': '',
                'seller_en': 'Dujana Auto Parts',
                'seller_am': 'ዱጃና የመኪና ዕቃዎች',
                'phone': '+251911234567',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name_en': 'Oil Filter Premium',
                'name_am': 'ፕሪሚየም የዘይት ፍልተር',
                'price': 450.00,
                'category_en': 'Filters',
                'category_am': 'ፍልተሮች',
                'stock': 50,
                'desc_en': 'Premium quality oil filter for extended engine protection. Removes contaminants efficiently.',
                'desc_am': 'ለተራዘመ ሞተር ጥበቃ ፕሪሚየም ጥራት ያለው የዘይት ፍልተር። ቆሻሻዎችን ያስወግዳል።',
                'image_path': '',
                'seller_en': 'Dujana Auto Parts',
                'seller_am': 'ዱጃና የመኪና ዕቃዎች',
                'phone': '+251911234567',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name_en': 'Spark Plug Set (4pcs)',
                'name_am': 'የስፓርክ ፕላግ ስብስብ (4 ቁርጥራጭ)',
                'price': 800.00,
                'category_en': 'Engine',
                'category_am': 'ሞተር',
                'stock': 30,
                'desc_en': 'High-quality iridium spark plugs for improved fuel efficiency. Set of 4.',
                'desc_am': 'ለተሻሻለ የነዳጅ ቆጣቢነት ከፍተኛ ጥራት ያለው ኢሪዲየም ስፓርክ ፕላጎች። 4 ቁርጥራጭ።',
                'image_path': '',
                'seller_en': 'Dujana Auto Parts',
                'seller_am': 'ዱጃና የመኪና ዕቃዎች',
                'phone': '+251922345678',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name_en': 'Car Battery 60Ah',
                'name_am': 'የመኪና ባትሪ 60Ah',
                'price': 5500.00,
                'category_en': 'Electrical',
                'category_am': 'ኤሌክትሪካል',
                'stock': 8,
                'desc_en': 'Maintenance-free 60Ah car battery with 2-year warranty. Suitable for most vehicles.',
                'desc_am': 'ጥገና-ነጻ 60Ah የመኪና ባትሪ ከ2 ዓመት ዋስትና ጋር። ለአብዛኛዎቹ ተሽከርካሪዎች ተስማሚ።',
                'image_path': '',
                'seller_en': 'Dujana Auto Parts',
                'seller_am': 'ዱጃና የመኪና ዕቃዎች',
                'phone': '+251933456789',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name_en': 'Air Filter Universal',
                'name_am': 'ዩኒቨርሳል የአየር ፍልተር',
                'price': 350.00,
                'category_en': 'Filters',
                'category_am': 'ፍልተሮች',
                'stock': 25,
                'desc_en': 'Universal air filter for improved airflow and engine protection. Easy installation.',
                'desc_am': 'ለተሻሻለ አየር ፍሰት ዩኒቨርሳል የአየር ፍልተር። ቀላል ጫዲ።',
                'image_path': '',
                'seller_en': 'Dujana Auto Parts',
                'seller_am': 'ዱጃና የመኪና ዕቃዎች',
                'phone': '+251911234567',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name_en': 'Shock Absorber Front',
                'name_am': 'የፊት ሾክ አብዞርበር',
                'price': 3200.00,
                'category_en': 'Suspension',
                'category_am': 'ሰስፔንሽን',
                'stock': 12,
                'desc_en': 'OEM-quality front shock absorber for smooth ride and handling. Sold per piece.',
                'desc_am': 'ለለስላሳ ጉዞ OEM ጥራት ያለው የፊት ሾክ አብዞርበር። በቁርጥ ቁርጥ ይሸጣል።',
                'image_path': '',
                'seller_en': 'Dujana Auto Parts',
                'seller_am': 'ዱጃና የመኪና ዕቃዎች',
                'phone': '+251944567890',
                'created_at': datetime.now().isoformat()
            }
        ]
        write_products(sample_products)


# ─── AUTH DECORATOR ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Unauthorized', 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated


# ─── ROUTES ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploads/images/<filename>')
def uploaded_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


@app.route('/api/products', methods=['GET'])
def get_products():
    products = read_products()
    search = request.args.get('search', '').lower()
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    if search:
        products = [p for p in products if
                    search in p['name_en'].lower() or
                    search in p['name_am'].lower() or
                    search in p['desc_en'].lower() or
                    search in p['category_en'].lower()]

    if category:
        products = [p for p in products if p['category_en'].lower() == category.lower()]

    if min_price is not None:
        products = [p for p in products if p['price'] >= min_price]

    if max_price is not None:
        products = [p for p in products if p['price'] <= max_price]

    return jsonify({'products': products, 'total': len(products)})


@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    products = read_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'product': product})


@app.route('/api/products', methods=['POST'])
@login_required
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['name_en', 'name_am', 'price', 'category_en', 'category_am']
    for field in required:
        if not str(data.get(field, '')).strip():
            return jsonify({'error': f'Field {field} is required'}), 400

    products = read_products()
    new_product = {
        'id': str(uuid.uuid4()),
        'name_en': data.get('name_en', ''),
        'name_am': data.get('name_am', ''),
        'price': float(data.get('price', 0)),
        'category_en': data.get('category_en', ''),
        'category_am': data.get('category_am', ''),
        'stock': int(data.get('stock', 0)),
        'desc_en': data.get('desc_en', ''),
        'desc_am': data.get('desc_am', ''),
        'image_path': data.get('image_path', ''),
        'seller_en': data.get('seller_en', ''),
        'seller_am': data.get('seller_am', ''),
        'phone': data.get('phone', ''),
        'created_at': datetime.now().isoformat()
    }
    products.append(new_product)
    write_products(products)
    return jsonify({'product': new_product, 'message': 'Product created successfully'}), 201


@app.route('/api/products/<product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    products = read_products()
    idx = next((i for i, p in enumerate(products) if p['id'] == product_id), None)
    if idx is None:
        return jsonify({'error': 'Product not found'}), 404

    p = products[idx]
    p['name_en'] = data.get('name_en', p['name_en'])
    p['name_am'] = data.get('name_am', p['name_am'])
    p['price'] = float(data.get('price', p['price']))
    p['category_en'] = data.get('category_en', p['category_en'])
    p['category_am'] = data.get('category_am', p['category_am'])
    p['stock'] = int(data.get('stock', p['stock']))
    p['desc_en'] = data.get('desc_en', p['desc_en'])
    p['desc_am'] = data.get('desc_am', p['desc_am'])
    p['image_path'] = data.get('image_path', p['image_path'])
    p['seller_en'] = data.get('seller_en', p['seller_en'])
    p['seller_am'] = data.get('seller_am', p['seller_am'])
    p['phone'] = data.get('phone', p['phone'])
    products[idx] = p
    write_products(products)
    return jsonify({'product': p, 'message': 'Product updated successfully'})


@app.route('/api/products/<product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    products = read_products()
    new_products = [p for p in products if p['id'] != product_id]
    if len(new_products) == len(products):
        return jsonify({'error': 'Product not found'}), 404
    write_products(new_products)
    return jsonify({'message': 'Product deleted successfully'})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    admin = check_admin_login(username, password)
    if not admin:
        return jsonify({'error': 'Invalid username or password'}), 401

    session.permanent = True
    session['admin_id'] = admin['id']
    session['admin_username'] = admin['username']
    session['admin_full_name'] = admin['full_name']
    session['admin_role'] = admin['role']

    return jsonify({
        'message': 'Login successful',
        'admin': {
            'id': admin['id'],
            'username': admin['username'],
            'full_name': admin['full_name'],
            'role': admin['role']
        }
    })


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'admin_id' in session:
        return jsonify({
            'authenticated': True,
            'admin': {
                'id': session['admin_id'],
                'username': session['admin_username'],
                'full_name': session['admin_full_name'],
                'role': session['admin_role']
            }
        })
    return jsonify({'authenticated': False})


@app.route('/api/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use jpg, jpeg, png, gif, or webp'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(IMAGES_DIR, unique_filename)
    file.save(filepath)

    return jsonify({
        'message': 'Image uploaded successfully',
        'image_path': f'/uploads/images/{unique_filename}',
        'filename': unique_filename
    })


@app.route('/api/categories', methods=['GET'])
def get_categories():
    products = read_products()
    categories = {}
    for p in products:
        key = p['category_en']
        if key not in categories:
            categories[key] = p['category_am']
    result = [{'en': k, 'am': v} for k, v in categories.items()]
    return jsonify({'categories': result})


if __name__ == '__main__':
    initialize_files()
    app.run(host='0.0.0.0', port = 5000)
