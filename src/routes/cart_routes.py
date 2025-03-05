from flask import Blueprint, request, jsonify
from src.services import cart_service, user_service
from src.models import Cart

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('/view', methods=['GET'])
def view_cart():
    """
    Retrieve the current cart items for a user.
    ---
    tags:
      - Cart
    parameters:
      - name: user_id
        in: query
        description: The ID of the user whose cart is being viewed.
        required: true
        type: integer
        example: 1
      - name: cart_id
        in: query
        description: The ID of the cart to view.
        required: true
        type: integer
        example: 10
    responses:
      200:
        description: A list of cart items.
        schema:
          type: array
          items:
            type: object
            properties:
              product_id:
                type: integer
                example: 101
              product_quantity:
                type: integer
                example: 3
      400:
        description: Missing parameters or an error occurred.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
    """
    user_id = request.args.get("user_id")
    cart_id = request.args.get("cart_id")
    if not user_id or not cart_id:
        return jsonify({"error": "Missing user_id or cart_id"}), 400

    try:
        user = user_service.get_user_by_id(int(user_id))
    except Exception:
        return jsonify({"error": "User not found"}), 400

    # Create a dummy Cart object with the given cart_id.
    dummy_cart = Cart(id=int(cart_id), user_id=user.id, items={})
    try:
        cart_items = cart_service.view_cart(dummy_cart, user)
        return jsonify(cart_items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/add', methods=['POST'])
def add_to_cart():
    """
    Add products to the user's shopping cart.
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: cartData
        description: Data containing the user ID and products to add.
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 1
            items:
              type: array
              description: A list of products with quantities to add.
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 101
                  product_quantity:
                    type: integer
                    example: 2
    responses:
      201:
        description: Cart updated successfully.
        schema:
          type: object
          properties:
            cart_id:
              type: integer
              example: 10
            user_id:
              type: integer
              example: 1
            items:
              type: object
              additionalProperties:
                type: integer
              example: {"101": 2, "102": 1}
      400:
        description: Error adding products to the cart.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing user_id or items"
    """
    data = request.get_json()
    user_id = data.get("user_id")
    items = data.get("items")
    
    if not user_id or not items:
        return jsonify({"error": "Missing user_id or items"}), 400

    try:
        user = user_service.get_user_by_id(int(user_id))
    except Exception:
        return jsonify({"error": "User not found"}), 400

    # Build the list of product tuples: (product_id, product_quantity)
    products = []
    for item in items:
        pid = item.get("product_id")
        qty = item.get("product_quantity")
        if pid is None or qty is None:
            return jsonify(
                {
                  "error": "Each item must have product_id and product_quantity"
                }
              ), 400
        products.append((pid, qty))

    try:
        # add_to_cart returns an updated Cart object with id and items dict.
        cart = cart_service.add_to_cart(user, products)
        return jsonify(
            {
              "cart_id": cart.id,
              "user_id": cart.user_id,
              "items": cart.items
            }
        ), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/order', methods=['POST'])
def place_order():
    """
    Place an order based on the user's current cart.
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: orderData
        description: Data containing the user ID and the cart ID to place an order for.
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 1
            cart_id:
              type: integer
              example: 10
    responses:
      201:
        description: Order placed successfully.
        schema:
          type: object
          properties:
            order_id:
              type: integer
              example: 100
            user_id:
              type: integer
              example: 1
            created_at:
              type: string
              format: date-time
              example: "2023-06-12T12:34:56"
            products:
              type: string
              description: JSON string of ordered products.
              example: "[{product_id: 101, product_quantity: 3}]"
      400:
        description: Error placing the order.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing user_id or cart_id"
    """
    data = request.get_json()
    user_id = data.get("user_id")
    cart_id = data.get("cart_id")
    if not user_id or not cart_id:
        return jsonify({"error": "Missing user_id or cart_id"}), 400

    try:
        user = user_service.get_user_by_id(int(user_id))
    except Exception:
        return jsonify({"error": "User not found"}), 400

    # Create a dummy Cart object for the given cart_id.
    dummy_cart = Cart(id=int(cart_id), user_id=user.id, items={})
    try:
        order = cart_service.place_order(dummy_cart, user)
        return jsonify({
            "order_id": order.id,
            "user_id": order.user_id,
            "created_at": order.created_at,
            "products": order.products
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
