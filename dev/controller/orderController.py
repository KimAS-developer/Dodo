from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import login_required, current_user

from dev import db
from domain.cart import Cart
from domain.order import Order

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()

    # Get user's cart items
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        return jsonify({'status': 'error', 'message': 'Your cart is empty'}), 400

    # Prepare order data
    order_data = {
        'delivery_type': data.get('delivery_type', 'pickup'),
        'payment_method': data.get('payment_method', 'cash'),
        'address': data.get('address'),
        'restaurant_id': data.get('restaurant_id') if data.get('delivery_type') == 'pickup' else None,
        'customer_info': {
            'name': current_user.name,
            'phone': current_user.phone,
            'email': current_user.email
        },
        'items': []
    }

    # Convert cart items to order items format
    for item in cart_items:
        item_data = {
            'type': 'pizza' if item.pizza else 'drink' if item.drink else 'desert',
            'name': item.pizza.name if item.pizza else item.drink.name if item.drink else item.desert.name,
            'quantity': item.quantity,
            'unit_price': item.get_price(),
            'total_price': item.get_total_price(),
            'size': item.size,
            'dough': item.dough,
            'extra_ingredients': item.extra_ingredients,
            'image': item.pizza.image_path if item.pizza else
            item.drink.image_path if item.drink else
            item.desert.image_path if item.desert else ''
        }
        order_data['items'].append(item_data)

    # Create new order
    new_order = Order(
        user_id=current_user.id,
        restaurant_id=order_data['restaurant_id'],
        delivery_type=order_data['delivery_type'],
        address=order_data['address'],
        payment_method=order_data['payment_method'],
        items=order_data['items'],
        customer_info=order_data['customer_info'],
        status='processing'
    )

    db.session.add(new_order)

    # Clear the cart
    Cart.query.filter_by(user_id=current_user.id).delete()

    db.session.commit()

    return jsonify({
        'status': 'success',
        'order_id': new_order.id,
        'redirect': url_for('orders.list_orders', order_id=new_order.id)
    })


@orders_bp.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    if not current_user.is_staff:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403

    order = Order.query.get_or_404(order_id)
    new_status = request.json.get('status')

    valid_statuses = ['processing', 'cooking', 'ready', 'delivered', 'canceled']
    if new_status not in valid_statuses:
        return jsonify({'status': 'error', 'message': 'Invalid status'}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Order status updated'})


@orders_bp.route('/orders')
@login_required
def list_orders():
    if current_user.is_cook():
        # Staff can see orders for their restaurant
        orders = Order.query.filter_by(restaurant_id=current_user.restaurant_id) \
            .order_by(Order.created_at.desc()).all()
    else:
        # Users can see their own orders
        orders = Order.query.filter_by(user_id=current_user.id) \
            .order_by(Order.created_at.desc()).all()

    return render_template('client_orders.html', orders=orders)


@orders_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == 'canceled':
        return jsonify({
            'status': 'error',
            'message': 'Заказ уже отменен'
        }), 400

    # Обновляем статус
    order.status = 'canceled'
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Order canceled successfully',
        'new_status': order.status
    })