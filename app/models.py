from dataclasses import dataclass
from config import db

@dataclass
class Stock(db.Model):
    __tablename__ = "STOCKS"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=True)
    acronym = db.Column(db.String(200), unique=True)
    stock_currency = db.Column(db.String(5))

    ownings = db.relationship('StockOwning', lazy=False)

    def __repr__(self):
        return '<Stock {}>'.format(self.name)


@dataclass
class StockOwning(db.Model):
    __tablename__ = "STOCK_OWNINGS"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock = db.Column(db.Integer, db.ForeignKey(Stock.id), nullable=False)
    quantity = db.Column(db.Float)
    buy_price = db.Column(db.Float)

    def __repr__(self):
        return '<Owning Stock ID {}>'.format(self.stock)