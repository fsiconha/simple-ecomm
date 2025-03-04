from flask import Flask
from db.database import init_db
from src.routes import cart_routes, user_routes, product_routes

def create_app() -> Flask:
    app = Flask(__name__)
    # Initialize the database
    init_db()
    # Register the blueprints
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(product_routes.bp)
    app.register_blueprint(cart_routes.bp)

    return app
