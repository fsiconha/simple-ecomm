from flask import Blueprint, request, jsonify
from src.services import product_service, user_service

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('', methods=['GET'])
def get_products():
    products = product_service.get_all_products()
    products_list = [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price
        } for p in products
    ]
    return jsonify(products_list), 200

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    product = product_service.get_product_by_id(product_id)
    if product:
        return jsonify(
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price
            }
        ), 200
    else:
        return jsonify({'error': 'Product not found'}), 404

@bp.route('/add', methods=['POST'])
def add_product():
    data = request.get_json()
    # For simplicity, user_id is provided in the request
    try:
        user = user_service.get_user_by_id(data.get('user_id'))
    except Exception:
        return jsonify({'error': 'User not found'}), 400
    name = data.get('name')
    description = data.get('description', '')
    price = data.get('price')
    try:
        product = product_service.add_product(user, name, description, price)
        return jsonify(
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price
            }
        ), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/edit/<int:product_id>', methods=['PUT'])
def edit_product(product_id: int):
    data = request.get_json()
    try:
        user = user_service.get_user_by_id(data.get('user_id'))
    except Exception:
        return jsonify({'error': 'User not found'}), 400
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    try:
        product = product_service.edit_product(
            user, product_id, name, description, price
        )
        return jsonify(
            {   'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price
            }
        ), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id: int):
    data = request.get_json()
    try:
        user = user_service.get_user_by_id(data.get('user_id'))
    except Exception:
        return jsonify({'error': 'User not found'}), 400
    try:
        product_service.delete_product(user, product_id)
        return jsonify({'message': 'Product deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
