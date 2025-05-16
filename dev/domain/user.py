from flask_login import UserMixin
from sqlalchemy.orm import relationship

from dev.extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    password = db.Column(db.String(100))
    role = db.Column(db.String(10))

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id', onupdate='CASCADE', ondelete='CASCADE'))
    restaurant = relationship("Restaurant", back_populates="users")

    def is_cook(self):
        return self.role == 'cook'

    def is_client(self):
        return self.role == 'client'

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password