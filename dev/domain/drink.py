from dev.extensions import db

class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255))
    price = db.Column(db.Integer, nullable=False)

