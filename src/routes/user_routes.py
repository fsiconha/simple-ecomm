from flask import Blueprint, request, jsonify
from src.services import user_service

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: user
        description: The user to be registered.
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "testuser"
            password:
              type: string
              example: "password123"
            role:
              type: string
              example: "regular"
    responses:
      201:
        description: User registered successfully.
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: "testuser"
            role:
              type: string
              example: "regular"
      400:
        description: Registration failed due to invalid input or error.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User already exists"
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'regular')
    try:
        user = user_service.register_user(username, password, role)
        return jsonify(
            {'id': user.id, 'username': user.username, 'role': user.role}
        ), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate an existing user.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: credentials
        description: The user login credentials.
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "testuser"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: User logged in successfully.
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: "testuser"
            role:
              type: string
              example: "regular"
      400:
        description: Login failed due to invalid credentials.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid username or password"
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    try:
        user = user_service.login_user(username, password)
        return jsonify(
            {'id': user.id, 'username': user.username, 'role': user.role}
        ), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
