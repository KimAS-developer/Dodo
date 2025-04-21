from dev.extensions import db

pizza_ingredient = db.Table(
    'pizza_ingredient',
    db.Column('pizza_id', db.Integer, db.ForeignKey('pizza.id', ondelete='CASCADE'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id', ondelete='CASCADE'), primary_key=True)
)