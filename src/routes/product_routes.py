from flask import Blueprint, request, jsonify
from src.services import product_service, user_service

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('', methods=['GET'])
def get_products():
    """
    Retrieve a list of all products.
    ---
    tags:
      - Products
    responses:
      200:
        description: A list of products.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Laptop"
              description:
                type: string
                example: "Gaming laptop"
              price:
                type: number
                format: float
                example: 1500.00
    """
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
    """
    Retrieve a specific product by its ID.
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: The ID of the product to retrieve.
    responses:
      200:
        description: A product object.
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Laptop"
            description:
              type: string
              example: "Gaming laptop"
            price:
              type: number
              format: float
              example: 1500.00
      404:
        description: Product not found.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Product not found"
    """
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
    """
    Add a new product to the catalog.
    ---
    tags:
      - Products
    parameters:
      - in: body
        name: product
        description: The product to add.
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 1
            name:
              type: string
              example: "Laptop"
            description:
              type: string
              example: "Gaming laptop"
            price:
              type: number
              format: float
              example: 1500.00
    responses:
      201:
        description: Product created successfully.
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Laptop"
            description:
              type: string
              example: "Gaming laptop"
            price:
              type: number
              format: float
              example: 1500.00
      400:
        description: Error creating product.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
    """
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
    """
    Edit an existing product.
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: The ID of the product to edit.
      - in: body
        name: product
        description: The new details for the product.
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 1
            name:
              type: string
              example: "Laptop Pro"
            description:
              type: string
              example: "High-end gaming laptop"
            price:
              type: number
              format: float
              example: 1700.00
    responses:
      200:
        description: Product updated successfully.
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Laptop Pro"
            description:
              type: string
              example: "High-end gaming laptop"
            price:
              type: number
              format: float
              example: 1700.00
      400:
        description: Error updating product.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
    """
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
    """
    Delete a product.
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: The ID of the product to delete.
      - in: body
        name: user
        description: The user performing the deletion.
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 1
    responses:
      200:
        description: Product deleted successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Product deleted"
      400:
        description: Error deleting product.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
    """
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
