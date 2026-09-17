"""
AGRITRADE - FLASK BACKEND
Flask + MySQL + Admin/User Login
"""
from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory
import os
from urllib.parse import quote_plus
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    session,
    redirect
)

from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Product, Customer, Purchase, Sale, Payment


# =========================================================
# FLASK APP
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=''
)
# Secret key for login sessions
app.secret_key = 'AgriTrade-Secret-Key-Change-This'
CORS(app, supports_credentials=True)


# =========================================================
# DATABASE
# =========================================================
DB_USER = os.environ.get("MYSQLUSER", "root")
DB_PASSWORD = os.environ.get("MYSQLPASSWORD", "")
DB_HOST = os.environ.get("MYSQLHOST", "localhost")
DB_PORT = os.environ.get("MYSQLPORT", "3306")
DB_NAME = os.environ.get("MYSQLDATABASE", "agritrade")

password = quote_plus(DB_PASSWORD)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# =========================================================
# LOGIN USERS
# =========================================================
# These are WEBSITE login credentials.
# They are NOT your MySQL credentials.
#
# Change these whenever you want.
# =========================================================

USERS = {
    'admin': {
        'password': generate_password_hash('Admin@123'),
        'role': 'admin'
    },

    'user': {
        'password': generate_password_hash('User@123'),
        'role': 'user'
    }
}


# =========================================================
# AUTHENTICATION HELPERS
# =========================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if 'username' not in session:
            return jsonify({
                'error': 'Login required'
            }), 401

        return function(*args, **kwargs)

    return wrapper


def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if 'username' not in session:
            return jsonify({
                'error': 'Login required'
            }), 401

        if session.get('role') != 'admin':
            return jsonify({
                'error': 'Admin access required'
            }), 403

        return function(*args, **kwargs)

    return wrapper


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route('/login')
def login_page():

    if 'username' in session:
        return redirect('/')

    return send_from_directory(
        app.static_folder,
        'login.html'
    )


# =========================================================
# LOGIN API
# =========================================================

@app.route('/api/login', methods=['POST'])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({
            'error': 'Username and password are required'
        }), 400

    user = USERS.get(username)

    if not user:
        return jsonify({
            'error': 'Invalid username or password'
        }), 401

    if not check_password_hash(user['password'], password):
        return jsonify({
            'error': 'Invalid username or password'
        }), 401

    session['username'] = username
    session['role'] = user['role']

    return jsonify({
        'message': 'Login successful',
        'username': username,
        'role': user['role']
    })


# =========================================================
# CURRENT USER
# =========================================================

@app.route('/api/me')
def current_user():

    return jsonify({
        'username': 'admin',
        'role': 'admin'
    })


# =========================================================
# LOGOUT
# =========================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


# =========================================================
# SERVE FRONTEND
# =========================================================

@app.route('/')
def serve_home():

    return send_from_directory(
        app.static_folder,
        'index.html'
    )


@app.route('/<path:filename>')
def serve_frontend_files(filename):
    return send_from_directory(app.static_folder, filename)


# =========================================================
# HELPERS
# =========================================================

def parse_date(value, default=None):

    if not value:
        return default or date.today()

    return datetime.strptime(
        value,
        '%Y-%m-%d'
    ).date()


def error(message, status=400):

    return jsonify({
        'error': message
    }), status


# =========================================================
# PRODUCTS
# =========================================================

@app.route('/api/products', methods=['GET'])
def get_products():

    search = request.args.get(
        'search',
        ''
    ).strip()

    query = Product.query

    if search:

        like = f'%{search}%'

        query = query.filter(
            (Product.product_name.ilike(like)) |
            (Product.category.ilike(like)) |
            (Product.variety.ilike(like))
        )

    products = query.order_by(
        Product.product_id
    ).all()

    return jsonify([
        p.to_dict()
        for p in products
    ])


@app.route('/api/products', methods=['POST'])
def create_product():

    data = request.get_json(
        silent=True
    ) or {}

    required = [
        'name',
        'category',
        'unit',
        'stock',
        'purchasePrice',
        'sellingPrice',
        'minimumStock'
    ]

    missing = [
        field
        for field in required
        if field not in data
    ]

    if missing:

        return error(
            f'Missing required field(s): {", ".join(missing)}'
        )

    product = Product(
        product_name=data['name'],
        category=data['category'],
        variety=data.get('variety'),
        unit=data['unit'],
        stock_quantity=data['stock'],
        purchase_price=data['purchasePrice'],
        selling_price=data['sellingPrice'],
        minimum_stock=data['minimumStock']
    )

    db.session.add(product)
    db.session.commit()

    return jsonify(
        product.to_dict()
    ), 201


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):

    product = Product.query.get(product_id)

    if not product:
        return error(
            'Product not found',
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    if 'name' in data:
        product.product_name = data['name']

    if 'category' in data:
        product.category = data['category']

    if 'variety' in data:
        product.variety = data['variety']

    if 'unit' in data:
        product.unit = data['unit']

    if 'stock' in data:
        product.stock_quantity = data['stock']

    if 'purchasePrice' in data:
        product.purchase_price = data['purchasePrice']

    if 'sellingPrice' in data:
        product.selling_price = data['sellingPrice']

    if 'minimumStock' in data:
        product.minimum_stock = data['minimumStock']

    db.session.commit()

    return jsonify(
        product.to_dict()
    )


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):

    product = Product.query.get(product_id)

    if not product:
        return error(
            'Product not found',
            404
        )

    db.session.delete(product)
    db.session.commit()

    return jsonify({
        'message': 'Product deleted'
    })


# =========================================================
# CUSTOMERS
# =========================================================

@app.route('/api/customers', methods=['GET'])
def get_customers():

    customers = Customer.query.order_by(
        Customer.customer_id
    ).all()

    return jsonify([
        c.to_dict()
        for c in customers
    ])


@app.route('/api/customers', methods=['POST'])
def create_customer():

    data = request.get_json(
        silent=True
    ) or {}

    if not data.get('name'):
        return error(
            'Missing required field: name'
        )

    customer = Customer(
        name=data['name'],
        phone=data.get('phone'),
        address=data.get('address')
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify(
        customer.to_dict()
    ), 201


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):

    customer = Customer.query.get(
        customer_id
    )

    if not customer:
        return error(
            'Customer not found',
            404
        )

    data = request.get_json(
        silent=True
    ) or {}

    if 'name' in data:
        customer.name = data['name']

    if 'phone' in data:
        customer.phone = data['phone']

    if 'address' in data:
        customer.address = data['address']

    db.session.commit()

    return jsonify(
        customer.to_dict()
    )


@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):

    customer = Customer.query.get(
        customer_id
    )

    if not customer:
        return error(
            'Customer not found',
            404
        )

    db.session.delete(customer)
    db.session.commit()

    return jsonify({
        'message': 'Customer deleted'
    })


# =========================================================
# PURCHASES
# =========================================================

@app.route('/api/purchases', methods=['GET'])
def get_purchases():

    purchases = Purchase.query.order_by(
        Purchase.purchase_id.desc()
    ).all()

    return jsonify([
        p.to_dict()
        for p in purchases
    ])


@app.route('/api/purchases', methods=['POST'])
def create_purchase():

    data = request.get_json(
        silent=True
    ) or {}

    required = [
        'supplier_name',
        'product_id',
        'quantity',
        'rate'
    ]

    missing = [
        field
        for field in required
        if field not in data
    ]

    if missing:

        return error(
            f'Missing required field(s): {", ".join(missing)}'
        )

    product = Product.query.get(
        data['product_id']
    )

    if not product:
        return error(
            'Invalid product_id',
            400
        )

    quantity = float(
        data['quantity']
    )

    rate = float(
        data['rate']
    )

    purchase = Purchase(
        supplier_name=data['supplier_name'],
        product_id=data['product_id'],
        quantity=quantity,
        rate=rate,
        total_amount=quantity * rate,
        purchase_date=parse_date(
            data.get('purchase_date')
        )
    )

    db.session.add(purchase)

    product.stock_quantity = (
        float(product.stock_quantity)
        + quantity
    )

    db.session.commit()

    return jsonify(
        purchase.to_dict()
    ), 201


# =========================================================
# SALES
# =========================================================

@app.route('/api/sales', methods=['GET'])
def get_sales():

    sales = Sale.query.order_by(
        Sale.sale_id.desc()
    ).all()

    return jsonify([
        s.to_dict()
        for s in sales
    ])


@app.route('/api/sales', methods=['POST'])
def create_sale():

    data = request.get_json(
        silent=True
    ) or {}

    required = [
        'customer_id',
        'product_id',
        'quantity',
        'rate'
    ]

    missing = [
        field
        for field in required
        if field not in data
    ]

    if missing:

        return error(
            f'Missing required field(s): {", ".join(missing)}'
        )

    customer = Customer.query.get(
        data['customer_id']
    )

    if not customer:
        return error(
            'Invalid customer_id',
            400
        )

    product = Product.query.get(
        data['product_id']
    )

    if not product:
        return error(
            'Invalid product_id',
            400
        )

    quantity = float(
        data['quantity']
    )

    rate = float(
        data['rate']
    )

    if quantity > float(
        product.stock_quantity
    ):

        return error(
            'Not enough stock available for this sale',
            400
        )

    sale = Sale(
        customer_id=data['customer_id'],
        product_id=data['product_id'],
        quantity=quantity,
        rate=rate,
        total_amount=quantity * rate,
        sale_date=parse_date(
            data.get('sale_date')
        ),
        status=data.get(
            'status',
            'Completed'
        )
    )

    db.session.add(sale)

    product.stock_quantity = (
        float(product.stock_quantity)
        - quantity
    )

    db.session.commit()

    return jsonify(
        sale.to_dict()
    ), 201


# =========================================================
# PAYMENTS
# =========================================================

@app.route('/api/payments', methods=['GET'])
def get_payments():

    payments = Payment.query.order_by(
        Payment.payment_id.desc()
    ).all()

    return jsonify([
        p.to_dict()
        for p in payments
    ])


@app.route('/api/payments', methods=['POST'])
def create_payment():

    data = request.get_json(
        silent=True
    ) or {}

    required = [
        'customer_id',
        'amount'
    ]

    missing = [
        field
        for field in required
        if field not in data
    ]

    if missing:

        return error(
            f'Missing required field(s): {", ".join(missing)}'
        )

    customer = Customer.query.get(
        data['customer_id']
    )

    if not customer:
        return error(
            'Invalid customer_id',
            400
        )

    if (
        data.get('sale_id')
        and not Sale.query.get(
            data['sale_id']
        )
    ):

        return error(
            'Invalid sale_id',
            400
        )

    payment = Payment(
        customer_id=data['customer_id'],
        sale_id=data.get('sale_id'),
        amount=data['amount'],
        payment_status=data.get(
            'payment_status',
            'Pending'
        ),
        payment_date=parse_date(
            data.get('payment_date')
        )
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify(
        payment.to_dict()
    ), 201


# =========================================================
# DASHBOARD
# =========================================================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():

    total_products = (
        db.session
        .query(
            func.count(
                Product.product_id
            )
        )
        .scalar()
        or 0
    )

    total_customers = (
        db.session
        .query(
            func.count(
                Customer.customer_id
            )
        )
        .scalar()
        or 0
    )

    total_suppliers = (
        db.session
        .query(
            func.count(
                func.distinct(
                    Purchase.supplier_name
                )
            )
        )
        .scalar()
        or 0
    )

    total_sales = (
        db.session
        .query(
            func.sum(
                Sale.total_amount
            )
        )
        .scalar()
        or 0
    )

    total_purchases = (
        db.session
        .query(
            func.sum(
                Purchase.total_amount
            )
        )
        .scalar()
        or 0
    )

    current_stock = (
        db.session
        .query(
            func.sum(
                Product.stock_quantity
            )
        )
        .scalar()
        or 0
    )

    low_stock = (
        Product.query
        .filter(
            Product.stock_quantity
            <= Product.minimum_stock
        )
        .order_by(
            Product.stock_quantity
        )
        .limit(6)
        .all()
    )

    recent_sales = (
        Sale.query
        .order_by(
            Sale.sale_date.desc(),
            Sale.sale_id.desc()
        )
        .limit(5)
        .all()
    )

    today = date.today()

    chart_labels = []
    chart_values = []

    for i in range(5, -1, -1):

        year = today.year
        month = today.month - i

        while month <= 0:
            month += 12
            year -= 1

        month_total = (
            db.session
            .query(
                func.sum(
                    Sale.total_amount
                )
            )
            .filter(
                func.year(
                    Sale.sale_date
                ) == year,
                func.month(
                    Sale.sale_date
                ) == month
            )
            .scalar()
            or 0
        )

        chart_labels.append(
            date(
                year,
                month,
                1
            ).strftime('%b')
        )

        chart_values.append(
            float(month_total)
        )

    return jsonify({

        'totalProducts': total_products,

        'totalCustomers': total_customers,

        'totalSuppliers': total_suppliers,

        'totalSales': float(
            total_sales
        ),

        'totalPurchases': float(
            total_purchases
        ),

        'currentStock': float(
            current_stock
        ),

        'lowStockProducts': [

            {
                'name': p.product_name,
                'category': p.category,
                'stock': float(
                    p.stock_quantity
                ),
                'unit': p.unit
            }

            for p in low_stock
        ],

        'recentTransactions': [

            {
                'invoice':
                    f'S-{10000 + s.sale_id}',

                'customer':
                    s.customer.name
                    if s.customer
                    else '',

                'product':
                    s.product.product_name
                    if s.product
                    else '',

                'date':
                    s.sale_date.strftime(
                        '%d %b %Y'
                    ),

                'quantity':
                    float(s.quantity),

                'unit':
                    s.product.unit
                    if s.product
                    else '',

                'amount':
                    float(s.total_amount),

                'status':
                    s.status
            }

            for s in recent_sales
        ],

        'salesChart': {
            'labels': chart_labels,
            'values': chart_values
        }

    })


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(e):

    if request.path.startswith('/api/'):

        return jsonify({
            'error': 'Not found'
        }), 404

    return e


@app.errorhandler(500)
def server_error(e):

    db.session.rollback()

    return jsonify({
        'error': 'Database connection error'
    }), 500


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
