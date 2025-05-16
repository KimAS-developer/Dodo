from dev.extensions import db
import json

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    delivery_type = db.Column(db.String(20), nullable=False)  # 'pickup' or 'delivery'
    address = db.Column(db.String(255))  # For delivery
    status = db.Column(db.String(20), default='В обработке')  # 'В обработке', 'Готовится', 'Готово', 'Отменен'
    payment_method = db.Column(db.String(20), nullable=False)  # 'cash' or 'card'
    _items = db.Column('items', db.Text)  # Store cart items as JSON

    user = db.relationship('User', backref='orders')
    restaurant = db.relationship('Restaurant', backref='orders')

    @property
    def items(self):
        if self._items:
            try:
                return json.loads(self._items)
            except json.JSONDecodeError:
                return []
        return []

    @items.setter
    def items(self, value):
        self._items = json.dumps(value) if value else None

    def get_total_price(self):
        total = 0
        for item in self.items:
            total += item.get('total_price', 0)
        return total