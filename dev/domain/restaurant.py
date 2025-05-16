from dev.extensions import db

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))

    users = db.relationship('User', back_populates='restaurant', cascade='all, delete-orphan')