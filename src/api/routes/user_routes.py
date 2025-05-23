from flask import Blueprint, jsonify, request
from api.models import db, User
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

user_bp = Blueprint(
    'user_custom', __name__, url_prefix='/')

CORS(user_bp)

bcrypt = Bcrypt()

@user_bp.route('/users_info', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([e.serialize_with_relations() for e in users]), 200

@user_bp.route('/home', methods=['GET'])
@jwt_required()
def private_route():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    response_body = {
        "message": f"Hola {user.email}, soy una ruta privada"
    }

    return jsonify(response_body), 200


@user_bp.route('/user/login', methods=["POST"])
def sing_in():
    data_request = request.get_json()

    if not 'email' in data_request or not 'password' in data_request:
        return jsonify({"error": "Los campos: email,password son requeridos"}), 400

    user = User.query.filter_by(email=data_request["email"]).first()

    if not user or not bcrypt.check_password_hash(user.password, data_request["password"]):
        return jsonify({"msg": "El email o la contraseña es incorrecto"}), 401

    try:
        access_token = create_access_token(identity=str(user.users_id))
        return jsonify({
            "token": access_token,
            "user": user.serialize()
        }), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "Error en el servido"}), 500


@user_bp.route('/user/create', methods=["POST"])
def create_user():
    data_request = request.get_json()

    if not 'email' in data_request or not 'password' in data_request:
        return jsonify({"error": "Los campos: email,password son requeridos"}), 400

    new_user = User(
        email=data_request["email"],
        password=bcrypt.generate_password_hash(
            data_request["password"]).decode('utf-8')
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "Se creo el usuario"}), 201
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "Error en el servido"}), 500

