import os
import uuid
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, send_from_directory, render_template

app = Flask(__name__)
app.secret_key = 'dujana-spare-parts-secret-key-2024'
app.permanent_session_lifetime = timedelta(days=7)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
IMAGES_DIR = os.path.join(UPLOADS_DIR, 'images')
PRODUCTS_FILE = os.path.join(UPLOADS_DIR, 'products.txt')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ADMIN_PASSWORD_HASH = hashlib.sha256('dujanaspare@123@'.encode()).hexdigest()
ADMIN_ID = 'dujana-admin-001'
ADMIN_USERNAME = 'dujana_admin'


def sha256_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
                    'id': parts[0], 'name_en': parts[1], 'name_am': parts[2],
                    'price': float(parts[3]), 'category_en': parts[4], 'category_am': parts[5],
                    'stock': int(parts[6]), 'desc_en': parts[7], 'desc_am': parts[8],
                    'image_path': parts[9], 'seller_en': parts[10], 'seller_am': parts[11],
                    'phone': parts[12], 'created_at': parts[13]
                })
    return products


def write_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        for p in products:
            f.write('|'.join([
                str(p.get('id','')), p.get('name_en',''), p.get('name_am',''),
                str(p.get('price',0)), p.get('category_en',''), p.get('category_am',''),
                str(p.get('stock',0)), p.get('desc_en',''), p.get('desc_am',''),
                p.get('image_path',''), p.get('seller_en',''), p.get('seller_am',''),
                p.get('phone',''), p.get('created_at','')
            ]) + '\n')


def initialize_files():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    if not os.path.exists(PRODUCTS_FILE) or os.path.getsize(PRODUCTS_FILE) == 0:
        now = datetime.now().isoformat()
        samples = [
            ('Brake Disc Set','የብሬክ ዲስክ ስብስብ',1250,'Brakes','ብሬኮች',15,
             'High-quality brake disc set compatible with most sedan vehicles. Excellent stopping power.',
             'ለሴዳን መኪናዎች ተስማሚ ከፍተኛ ጥራት ያለው የብሬክ ዲስክ ስብስብ።'),
            ('Oil Filter Premium','ፕሪሚየም ዘይት ማጣሪያ',450,'Filters','ማጣሪያዎች',40,
             'Premium oil filter removing contaminants for smooth engine operation. Universal fit.',
             'ሞተርዎ ለስላሳ እንዲሰራ ቆሻሻዎችን የሚያስወግድ ፕሪሚየም ዘይት ማጣሪያ።'),
            ('Spark Plug Set (4pcs)','ስፓርክ ፕላግ ስብስብ',680,'Engine','ሞተር',25,
             'Iridium spark plugs for improved fuel efficiency and peak engine performance.',
             'የተሻሻለ የነዳጅ ቆጣቢነት ለማሻሻል ከፍተኛ አፈጻጸም ያለው ስፓርክ ፕላግ።'),
            ('Rear Shock Absorber','የኋላ ሾክ አብዞርበር',2100,'Suspension','ሰስፐንሽን',8,
             'OEM-grade rear shock absorber for smooth ride and precise handling.',
             'ለስላሳ ጉዞ እና ትክክለኛ አያያዝ OEM-ደረጃ የኋላ ሾክ አብዞርበር።'),
            ('Timing Belt Kit','የታይሚንግ ቤልት ኪት',1850,'Engine','ሞተር',12,
             'Complete timing belt kit with tensioner and idler pulleys for engine timing accuracy.',
             'የሞተር ታይሚንግ ትክክለኛነት ለሙሉ ታይሚንግ ቤልት ኪት ከቴንሽነር ጋር።'),
            ('Radiator Coolant 4L','ራዲያተር ኩላንት 4 ሊትር',320,'Cooling','ማቀዝቀዣ',50,
             'High-performance engine coolant protecting against overheating and corrosion.',
             'ከከፍተኛ ሙቀት እና ዝገት ጥበቃ ከፍተኛ አፈጻጸም ያለው የሞተር ኩላንት።'),
        ]
        write_products([{
            'id': str(uuid.uuid4()), 'name_en': s[0], 'name_am': s[1], 'price': s[2],
            'category_en': s[3], 'category_am': s[4], 'stock': s[5],
            'desc_en': s[6], 'desc_am': s[7], 'image_path': '',
            'seller_en': 'Dujana Auto Parts', 'seller_am': 'ዱጃና ኦቶ ፓርትስ',
            'phone': '+251911234567', 'created_at': now
        } for s in samples])


initialize_files()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({'success': True, 'products': read_products()})

@app.route('/api/products/<pid>', methods=['GET'])
def get_product(pid):
    p = next((x for x in read_products() if x['id'] == pid), None)
    if not p: return jsonify({'success': False, 'message': 'Not found'}), 404
    return jsonify({'success': True, 'product': p})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if sha256_hash(data.get('password', '')) == ADMIN_PASSWORD_HASH:
        session.permanent = True
        session['admin_id'] = ADMIN_ID
        session['admin_username'] = ADMIN_USERNAME
        return jsonify({'success': True, 'admin': {'username': ADMIN_USERNAME, 'full_name': 'Dujana Administrator'}})
    return jsonify({'success': False, 'message': 'Incorrect password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'admin_id' in session:
        return jsonify({'success': True, 'authenticated': True, 'username': session.get('admin_username')})
    return jsonify({'success': True, 'authenticated': False})

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    if 'admin_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    file = request.files.get('image')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file'}), 400
    fn = f"{uuid.uuid4()}_{file.filename}"
    file.save(os.path.join(IMAGES_DIR, fn))
    return jsonify({'success': True, 'image_path': f'/uploads/images/{fn}'})

@app.route('/api/products', methods=['POST'])
def create_product():
    if 'admin_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json()
    for f in ['name_en','name_am','price','category_en','category_am']:
        if not data.get(f): return jsonify({'success': False, 'message': f'Missing: {f}'}), 400
    p = {'id': str(uuid.uuid4()), 'name_en': data['name_en'], 'name_am': data['name_am'],
         'price': float(data['price']), 'category_en': data['category_en'], 'category_am': data['category_am'],
         'stock': int(data.get('stock',0)), 'desc_en': data.get('desc_en',''), 'desc_am': data.get('desc_am',''),
         'image_path': data.get('image_path',''), 'seller_en': data.get('seller_en',''),
         'seller_am': data.get('seller_am',''), 'phone': data.get('phone',''), 'created_at': datetime.now().isoformat()}
    products = read_products(); products.append(p); write_products(products)
    return jsonify({'success': True, 'product': p}), 201

@app.route('/api/products/<pid>', methods=['PUT'])
def update_product(pid):
    if 'admin_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json(); products = read_products()
    idx = next((i for i,x in enumerate(products) if x['id']==pid), None)
    if idx is None: return jsonify({'success': False, 'message': 'Not found'}), 404
    p = products[idx]
    for k in ['name_en','name_am','category_en','category_am','desc_en','desc_am','seller_en','seller_am','phone','image_path']:
        p[k] = data.get(k, p[k])
    p['price'] = float(data.get('price', p['price'])); p['stock'] = int(data.get('stock', p['stock']))
    products[idx] = p; write_products(products)
    return jsonify({'success': True, 'product': p})

@app.route('/api/products/<pid>', methods=['DELETE'])
def delete_product(pid):
    if 'admin_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    products = read_products(); new = [x for x in products if x['id']!=pid]
    if len(new)==len(products): return jsonify({'success': False, 'message': 'Not found'}), 404
    write_products(new); return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
