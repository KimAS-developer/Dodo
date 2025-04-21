from flask import Blueprint, render_template

from dev import db
from domain.desert import Desert
from domain.drink import Drink
from domain.ingredient import Ingredient
from domain.pizza import Pizza

mainPage = Blueprint('mainPage', __name__)

@mainPage.route('/')
def index():
    pizzas = Pizza.query.all()
    drinks = Drink.query.all()
    deserts = Desert.query.all()
    ingredients = Ingredient.query.all()
    return render_template('mainPage.html',
                           pizzas=pizzas,
                           drinks=drinks,
                           deserts=deserts,
                           ingredients=ingredients
                           )