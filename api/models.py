from main import db, admin
from datetime import datetime
from users import User
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"<{self.__name__} {self.id}>"


class SoftDeletedModelBase:
    deleted = db.Column(db.Boolean(), default=False)


class TimeStampModelBase:
    created_at = db.Column(db.DateTime(), default=datetime.now)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.now)


class CreatorModelBase:
    @declared_attr
    def created_by(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Product(CreatorModelBase, TimeStampModelBase, BaseModel):
    name = db.Column(db.String(250))
    description = db.Column(db.String(250))
    amount_min = db.Column(db.Integer)
    amount_total = db.Column(db.Integer)
    ''' shopping = db.relationship('Shopping', backref='product')
    score = db.relationship('Score', backref='product')
    output = db.relationship('Output', backref='product')'''

    def __init__(self, name, description, amount_min, amount_total, created_by):
        self.name = name
        self.description = description
        self.amount_min = amount_min
        self.amount_total = amount_total
        self.created_by = created_by

    def __repr__(self):
        return f"<{self.__name__} {self.name}>"


class Shopping(CreatorModelBase, TimeStampModelBase, BaseModel):
    amount = db.Column(db.Integer)
    product = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __init__(self, amount, product):
        self.amount = amount
        self.product = product

    def __repr__(self):
        return f"<{self.__name__} {self.product.name}>"


class Score(CreatorModelBase, TimeStampModelBase, BaseModel):
    product = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __init__(self, amount, product):
        self.amount = amount
        self.product = product

    def __repr__(self):
        return f"<{self.__name__} {self.product.name}>"


class Output(CreatorModelBase, TimeStampModelBase, BaseModel):
    product = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __init__(self, product, amount):
        self.product = product
        self.amount = amount

    def __repr__(self):
        return f"<{self.__name__} {self.product.name}>"


admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Shopping, db.session))
admin.add_view(ModelView(Score, db.session))
admin.add_view(ModelView(Output, db.session))
