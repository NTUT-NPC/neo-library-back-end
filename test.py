from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import sys

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'NTUT_NPC'  # Change this!
jwt = JWTManager(app)


@jwt.invalid_token_loader
def invalid_token_callback(expired_token):
    return "", 401

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/login', methods=['POST'])
def login():
    # if not request.is_json:
    #     return jsonify({"msg": "Missing JSON in request"}), 400

    user_info = dict(request.form)
    print(user_info, sys.stdout)
    # post 到 威任的後端，並把資料存進 json file

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user_info)
    return access_token


# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    print(type(current_user), sys.stdout)
    return jsonify(logged_in_as=current_user), 200


if __name__ == '__main__':
    app.run()
