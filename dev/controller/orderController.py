from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from dev import db
from domain.order import Order

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
@login_required
def view_orders():
    if current_user.is_client():
        # Client view: show their own orders
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
        return render_template('client_orders.html', orders=orders)
    elif current_user.is_cook():
        # Cook view: show orders for their restaurant
        orders = Order.query.filter_by(restaurant_id=current_user.restaurant_id).order_by(Order.id.desc()).all()
        return render_template('cook_orders.html', orders=orders)
    else:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

@orders_bp.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    if not current_user.is_client():
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        return jsonify({'status': 'error', 'message': 'Order not found'}), 404

    if order.status == 'Готово' or order.status == 'Отменен':
        return jsonify({'status': 'error', 'message': 'Cannot cancel order in this status'}), 400

    order.status = 'Отменен'
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Order cancelled'})

@orders_bp.route('/api/orders/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_order(order_id):
    if not current_user.is_cook():
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    order = Order.query.filter_by(id=order_id, restaurant_id=current_user.restaurant_id).first()
    if not order:
        return jsonify({'status': 'error', 'message': 'Order not found'}), 404

    if order.status != 'В обработке':
        return jsonify({'status': 'error', 'message': 'Order cannot be accepted'}), 400

    order.status = 'Готовится'
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Order accepted'})

@orders_bp.route('/api/orders/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    if not current_user.is_cook():
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    order = Order.query.filter_by(id=order_id, restaurant_id=current_user.restaurant_id).first()
    if not order:
        return jsonify({'status': 'error', 'message': 'Order not found'}), 404

    if order.status != 'Готовится':
        return jsonify({'status': 'error', 'message': 'Order cannot be completed'}), 400

    order.status = 'Готово'
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Order completed'})