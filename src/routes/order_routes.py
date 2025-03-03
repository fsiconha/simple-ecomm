from flask import Blueprint, request, jsonify
from src.services import order_service, user_service

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route('/view_cart', methods=['GET'])
def view_cart():
    user_id = request.args.get('user_id')
    try:
        user = user_service.get_user_by_id(int(user_id))
    except Exception:
        return jsonify({'error': 'User not found'}), 400
    cart_items = order_service.view_cart(user)
    items = [
        {
            'id': item.id,
            'product_id': item.product_id,
            'quantity': item.quantity
        } for item in cart_items
    ]
    return jsonify(items), 200

@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    try:
        user = user_service.get_user_by_id(int(user_id))
    except Exception:
        return jsonify({'error': 'User not found'}), 400
    try:
        cart_item = order_service.add_to_cart(user, product_id, quantity)
        return jsonify(
            {
                'id': cart_item.id,
                'product_id': cart_item.product_id,
                'quantity': cart_item.quantity
            }
        ), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/order', methods=['POST'])
def place_order():
    data = request.get_json()
    user_id = data.get('user_id')
    try:
        user = user_service.get_user_by_id(int(user_id))
    except Exception:
        return jsonify({'error': 'User not found'}), 400
    try:
        order = order_service.place_order(user)
        return jsonify(
            {'order_id': order.id, 'created_at': order.created_at}
        ), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
