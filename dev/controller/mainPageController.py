import json

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user

from dev.extensions import db
from domain.cart import Cart
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
                           ingredients=ingredients,
                           is_authenticated=current_user.is_authenticated
                           )


@mainPage.route('/add_to_cart/<item_type>/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_type, item_id):
    if item_type not in ['pizza', 'drink', 'desert']:
        return jsonify({'success': False, 'message': 'Неверный тип товара'})

    try:
        # Verify JSON data format
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Неверный формат данных'})

        data = request.get_json()
        if data is None:
            return jsonify({'success': False, 'message': 'Неверные данные'})

        # Create a new cart item
        cart_item = Cart(user_id=current_user.id, quantity=1)

        # Fill data based on item type
        if item_type == 'pizza':
            cart_item.pizza_id = item_id
            cart_item.size = data.get('size', '25')
            cart_item.dough = data.get('dough', 'traditional')

            # Properly handle extra ingredients
            extra_ingredients = data.get('extraIngredients', [])
            if extra_ingredients:
                # If we have just ingredient IDs
                if isinstance(extra_ingredients[0], int):
                    # Store the IDs directly
                    cart_item.extra_ingredients = json.dumps(extra_ingredients)
                # If we have complete ingredient objects
                elif isinstance(extra_ingredients[0], dict):
                    # Store the full objects
                    cart_item.extra_ingredients = json.dumps(extra_ingredients)
        elif item_type == 'drink':
            cart_item.drink_id = item_id
        elif item_type == 'desert':
            cart_item.desert_id = item_id

        # Check if this item already exists in the cart
        existing_query = Cart.query.filter_by(
            user_id=current_user.id,
            pizza_id=cart_item.pizza_id if item_type == 'pizza' else None,
            drink_id=cart_item.drink_id if item_type == 'drink' else None,
            desert_id=cart_item.desert_id if item_type == 'desert' else None
        )

        # Add more specific filters for pizza options
        if item_type == 'pizza':
            existing_query = existing_query.filter_by(
                size=cart_item.size,
                dough=cart_item.dough
            )

            # For extra ingredients, we need special handling
            if cart_item._extra_ingredients:
                existing_query = existing_query.filter_by(
                    _extra_ingredients=cart_item._extra_ingredients
                )
            else:
                existing_query = existing_query.filter(
                    (Cart._extra_ingredients.is_(None)) | (Cart._extra_ingredients == '')
                )

        existing_item = existing_query.first()

        if existing_item:
            existing_item.quantity += 1
            db.session.commit()
        else:
            db.session.add(cart_item)
            db.session.commit()

        return jsonify({'success': True, 'message': 'Товар добавлен в корзину'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})