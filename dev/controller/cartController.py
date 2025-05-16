import json

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from dev import db
from domain.cart import Cart
from domain.ingredient import Ingredient
from domain.restaurant import Restaurant

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    restaurants = Restaurant.query.all()

    # Process extra ingredients for each cart item
    for item in cart_items:
        if item.pizza and item._extra_ingredients:
            try:
                # If stored as JSON string with IDs, fetch the actual ingredients
                raw_data = json.loads(item._extra_ingredients)

                # If it's a list of IDs, convert to ingredient objects
                if isinstance(raw_data, list) and raw_data and isinstance(raw_data[0], int):
                    ingredient_ids = raw_data
                    item.extra_ingredients = Ingredient.query.filter(
                        Ingredient.id.in_(ingredient_ids)
                    ).all()
                # If already full ingredient objects with data, keep as is
                else:
                    item.extra_ingredients = raw_data
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error processing extra ingredients for item {item.id}: {e}")
                item.extra_ingredients = []
        else:
            item.extra_ingredients = []

    # Calculate total price
    total = sum(item.get_total_price() for item in cart_items if item is not None)

    return render_template('cart.html',
                           cart_items=cart_items,
                           restaurants=restaurants,
                           total_price=total)

@cart_bp.route('/api/cart/items/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def handle_cart_item(item_id):
    try:
        item = Cart.query.filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404

        if request.method == 'PUT':
            data = request.get_json()
            action = data.get('action')

            if action == 'increase':
                item.quantity += 1
            elif action == 'decrease':
                if item.quantity > 1:
                    item.quantity -= 1
                else:
                    db.session.delete(item)
                    db.session.commit()
                    return jsonify({'status': 'removed'})

            db.session.commit()
            return jsonify({
                'status': 'updated',
                'quantity': item.quantity,
                'price': item.get_price(),  # Добавляем цену за единицу
                'total_price': item.get_total_price()
            })

        elif request.method == 'DELETE':
            db.session.delete(item)
            db.session.commit()
            return jsonify({'status': 'removed'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500