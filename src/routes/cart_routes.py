from flask import Blueprint, request, jsonify
from src.services import cart_service, user_service
from db.models import Cart

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('/view', methods=['GET'])
def view_cart():
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
    Adds products to the user's shopping cart.
    Expects a JSON body with:
    {
        "user_id": int,
        "items": [
            {"product_id": int, "product_quantity": int},
            ...
        ]
    }
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
            return jsonify({"error": "Each item must have product_id and product_quantity"}), 400
        products.append((pid, qty))
    
    try:
        # add_to_cart returns an updated Cart object with id and items dict.
        cart = cart_service.add_to_cart(user, products)
        return jsonify({
            "cart_id": cart.id,
            "user_id": cart.user_id,
            "items": cart.items
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/order', methods=['POST'])
def place_order():
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
