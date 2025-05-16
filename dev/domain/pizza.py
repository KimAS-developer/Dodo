from dev.extensions import db
from domain.ingredient import Ingredient
from domain.pizza_ingredient import pizza_ingredient


class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255))
    price = db.Column(db.Integer, nullable=False)

    ingredients = db.relationship(
        Ingredient,
        secondary=pizza_ingredient,
        backref='pizzas',
        lazy='joined'  # Жадная загрузка по умолчанию
    )


