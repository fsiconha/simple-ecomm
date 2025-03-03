from flask import Blueprint, request, jsonify
from src.services import user_service

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/register', methods=['POST'])
def register():
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
