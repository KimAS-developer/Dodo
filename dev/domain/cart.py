from dev.extensions import db
import json
from domain.ingredient import Ingredient  # Import Ingredient model


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'))
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
    desert_id = db.Column(db.Integer, db.ForeignKey('desert.id'))
    quantity = db.Column(db.Integer, default=1)
    size = db.Column(db.String(10))
    dough = db.Column(db.String(20))
    _extra_ingredients = db.Column('extra_ingredients', db.Text)  # Stored as JSON text

    # Relationships
    pizza = db.relationship('Pizza')
    drink = db.relationship('Drink')
    desert = db.relationship('Desert')

    # Надбавки за размер пиццы
    SIZE_PRICE_ADJUSTMENTS = {
        '25': 0,  # Базовая цена для 25см
        '30': 200,  # +200 рублей за 30см
        '35': 350  # +350 рублей за 35см
    }

    @property
    def extra_ingredients(self):
        """Convert stored JSON string to a list of ingredient dictionaries or objects"""
        if not self._extra_ingredients:
            return []

        try:
            ingredients_data = json.loads(self._extra_ingredients)

            # Check if we have received a list of dictionaries
            if isinstance(ingredients_data, list) and ingredients_data:
                # If it's a simple list of IDs, fetch the actual ingredients
                if isinstance(ingredients_data[0], int):
                    return Ingredient.query.filter(Ingredient.id.in_(ingredients_data)).all()

                # If they're already dictionaries with all needed data, return as is
                elif isinstance(ingredients_data[0], dict):
                    return ingredients_data

            return []
        except (json.JSONDecodeError, Exception):
            return []

    @extra_ingredients.setter
    def extra_ingredients(self, value):
        """Store ingredients list as JSON string"""
        if value:
            if isinstance(value, str):
                # Already a JSON string
                self._extra_ingredients = value
            else:
                # Convert to JSON string
                self._extra_ingredients = json.dumps(value)
        else:
            self._extra_ingredients = None

    def get_price(self):
        """Calculate the price of the item including extras and size adjustments"""
        price = 0
        if self.pizza:
            # Базовая цена пиццы
            price = self.pizza.price

            # Добавляем надбавку за размер пиццы
            if self.size and self.size in self.SIZE_PRICE_ADJUSTMENTS:
                price += self.SIZE_PRICE_ADJUSTMENTS[self.size]

            # Добавляем цену за дополнительные ингредиенты
            extras = self.extra_ingredients  # Используем property
            if extras:
                # Обрабатываем как объекты, так и словари
                if extras and hasattr(extras[0], 'price'):
                    # Список объектов Ingredient
                    price += sum(ing.price for ing in extras)
                elif extras and isinstance(extras[0], dict):
                    # Список словарей
                    price += sum(ing.get('price', 0) for ing in extras)
        elif self.drink:
            price = self.drink.price
        elif self.desert:
            price = self.desert.price
        return price

    def get_total_price(self):
        return self.get_price() * self.quantity