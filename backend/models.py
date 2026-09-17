"""
AGRITRADE - DATABASE MODELS
===========================
One simple SQLAlchemy class per table. Each class also has a
to_dict() helper so app.py can turn a row into JSON easily.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    variety = db.Column(db.String(100))
    unit = db.Column(db.String(20), nullable=False, default='kg')
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    selling_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock_quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    minimum_stock = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # NOTE: keys are camelCase here on purpose - they match the
    # field names the existing products.html / script.js already use,
    # so the frontend needed almost no changes.
    def to_dict(self):
        return {
            'id': self.product_id,
            'name': self.product_name,
            'category': self.category,
            'variety': self.variety,
            'unit': self.unit,
            'purchasePrice': float(self.purchase_price),
            'sellingPrice': float(self.selling_price),
            'stock': float(self.stock_quantity),
            'minimumStock': float(self.minimum_stock)
        }


class Purchase(db.Model):
    __tablename__ = 'purchases'

    purchase_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(150), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    rate = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)

    product = db.relationship('Product')

    def to_dict(self):
        return {
            'purchase_id': self.purchase_id,
            'supplier_name': self.supplier_name,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'quantity': float(self.quantity),
            'rate': float(self.rate),
            'total_amount': float(self.total_amount),
            'purchase_date': self.purchase_date.isoformat()
        }


class Sale(db.Model):
    __tablename__ = 'sales'

    sale_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    rate = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Completed')

    customer = db.relationship('Customer')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'sale_id': self.sale_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'quantity': float(self.quantity),
            'rate': float(self.rate),
            'total_amount': float(self.total_amount),
            'sale_date': self.sale_date.isoformat(),
            'status': self.status
        }


class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.sale_id'))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='Pending')
    payment_date = db.Column(db.Date, nullable=False)

    customer = db.relationship('Customer')

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'sale_id': self.sale_id,
            'amount': float(self.amount),
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat()
        }
