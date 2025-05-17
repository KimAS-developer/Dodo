from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import login_required, current_user

from dev import db
from domain.cart import Cart
from domain.order import Order

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    # Получаем данные из запроса
    data = request.get_json()

    # Проверяем наличие товаров в корзине
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'status': 'error', 'message': 'Ваша корзина пуста'}), 400

    # Проверяем обязательные поля в зависимости от типа доставки
    delivery_type = data.get('delivery_type', 'pickup')
    payment_method = data.get('payment_method', 'cash')

    if delivery_type == 'delivery' and not data.get('address'):
        return jsonify({'status': 'error', 'message': 'Укажите адрес доставки'}), 400

    if delivery_type == 'pickup' and not data.get('restaurant_id'):
        return jsonify({'url_forstatus': 'error', 'message': 'Выберите ресторан для самовывоза'}), 400

    # Подготавливаем данные заказа
    order_data = {
        'delivery_type': delivery_type,
        'payment_method': payment_method,
        'address': data.get('address'),
        'restaurant_id': data.get('restaurant_id') if delivery_type == 'pickup' else 1,
        'customer_info': {
            'name': current_user.name,
            'phone': current_user.phone,
            'email': current_user.email
        },
        'items': []
    }

    # Конвертируем товары из корзины в формат заказа
    for item in cart_items:
        product = item.pizza or item.drink or item.desert
        if not product:
            continue

        item_data = {
            'type': 'pizza' if item.pizza else 'drink' if item.drink else 'desert',
            'name': product.name,
            'quantity': item.quantity,
            'unit_price': item.get_price(),
            'total_price': item.get_total_price(),
            'size': item.size,
            'dough': item.dough,
            'extra_ingredients': item.extra_ingredients,
            'image': product.image_path if hasattr(product, 'image_path') else ''
        }
        order_data['items'].append(item_data)

    # Создаем новый заказ
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

    try:
        db.session.add(new_order)
        # Очищаем корзину
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Произошла ошибка при оформлении заказа',
            'error': str(e)
        }), 500

    return jsonify({
        'status': 'success',
        'order_id': new_order.id,
        'redirect': url_for('orders.list_orders')
    })


@orders_bp.route('/orders')
@login_required
def list_orders():
    if current_user.is_cook():
        # Для поваров - активные заказы ресторана (исключая финальные статусы)
        orders = Order.query.filter(
            Order.restaurant_id == current_user.restaurant_id,
            ~Order.status.in_(['delivered', 'received', 'canceled'])
        ).order_by(Order.created_at.desc()).all()
        return render_template('cook_orders.html', orders=orders)
    else:
        # Для клиентов - их активные заказы
        orders = Order.query.filter(
            Order.user_id == current_user.id,
            ~Order.status.in_(['delivered', 'received', 'canceled'])
        ).order_by(Order.created_at.desc()).all()
        return render_template('client_orders.html', orders=orders)


@orders_bp.route('/history')
@login_required
def order_history():
    if current_user.is_cook():
        # История заказов ресторана (только финальные статусы)
        orders = Order.query.filter(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status.in_(['delivered', 'received', 'canceled'])
        ).order_by(Order.created_at.desc()).all()
    else:
        # История заказов клиента
        orders = Order.query.filter(
            Order.user_id == current_user.id,
            Order.status.in_(['delivered', 'received', 'canceled'])
        ).order_by(Order.created_at.desc()).all()

    return render_template('order_history.html', orders=orders)


@orders_bp.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    if not current_user.is_cook():
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403

    order = Order.query.get_or_404(order_id)

    # Проверяем, что заказ принадлежит ресторану повара
    if order.restaurant_id != current_user.restaurant_id:
        return jsonify({'status': 'error', 'message': 'Этот заказ не из вашего ресторана'}), 403

    new_status = request.json.get('status')

    # Базовые допустимые статусы
    valid_statuses = ['processing', 'cooking', 'ready', 'courier']

    # Добавляем финальный статус в зависимости от типа доставки
    final_status = order.get_final_status()
    valid_statuses.append(final_status)

    if new_status not in valid_statuses:
        return jsonify({'status': 'error', 'message': 'Недопустимый статус для этого типа заказа'}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Статус заказа обновлен',
        'new_status': new_status,
        'status_display': order.get_status_display()
    })


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