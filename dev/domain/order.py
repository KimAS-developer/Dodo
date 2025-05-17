import json
from datetime import datetime

from dev.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    delivery_type = db.Column(db.String(20), nullable=False)  # 'pickup' или 'delivery'
    address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='processing')  # processing, cooking, ready, canceled, delivered
    payment_method = db.Column(db.String(20), nullable=False)  # 'cash' или 'card'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    _items = db.Column('items', db.Text)  # JSON с товарами
    _customer_info = db.Column('customer_info', db.Text)  # JSON с информацией о клиенте

    # Relationships
    user = db.relationship('User', backref='orders')
    restaurant = db.relationship('Restaurant', backref='orders')

    @property
    def items(self):
        """Получаем список товаров из JSON"""
        if not self._items:
            return []
        try:
            items = json.loads(self._items)
            # Добавляем отображаемые названия для типов теста
            for item in items:
                if 'dough' in item:
                    item['dough_display'] = self.get_dough_display(item['dough'])
            return items
        except json.JSONDecodeError:
            return []

    @items.setter
    def items(self, value):
        """Сохраняем список товаров как JSON"""
        self._items = json.dumps(value) if value else None

    @property
    def customer_info(self):
        """Получаем информацию о клиенте из JSON"""
        if not self._customer_info:
            return {}
        try:
            return json.loads(self._customer_info)
        except json.JSONDecodeError:
            return {}

    @customer_info.setter
    def customer_info(self, value):
        """Сохраняем информацию о клиенте как JSON"""
        self._customer_info = json.dumps(value) if value else None

    def get_total_price(self):
        """Общая сумма заказа"""
        return sum(item.get('total_price', 0) for item in self.items)

    @staticmethod
    def get_dough_display(dough_type):
        """Отображаемое название типа теста"""
        if dough_type is None:
            return "Не указано"

        dough_types = {
            'traditional': 'Традиционное',
            'thin': 'Тонкое'
        }
        return dough_types.get(dough_type, dough_type.capitalize() if dough_type else "Не указано")

    def get_status_display(self):
        """Отображаемое название статуса"""
        statuses = {
            'processing': 'В обработке',
            'cooking': 'Готовится',
            'ready': 'Готово',
            'canceled': 'Отменен',
            'delivered': 'Доставлен'
        }
        return statuses.get(self.status, self.status)

    def get_delivery_type_display(self):
        """Отображаемое название типа доставки"""
        return 'Самовывоз' if self.delivery_type == 'pickup' else 'Доставка'

    def get_payment_method_display(self):
        """Отображаемое название способа оплаты"""
        return 'Наличными' if self.payment_method == 'cash' else 'Картой'
