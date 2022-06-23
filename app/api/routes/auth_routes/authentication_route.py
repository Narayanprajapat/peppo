from flask import Blueprint, request

from app.api.auth.authentication import user_registered_api, account_verification_api, user_login_api

authentication = Blueprint('authentication', __name__, static_folder='static', template_folder='templates')


@authentication.route('/api/user/registered', methods=['POST'])
def user_registered():
    return user_registered_api(request)


@authentication.route('/api/user/account/verification', methods=['POST'])
def account_verification():
    return account_verification_api(request)


@authentication.route('/api/user/login', methods=['POST'])
def user_login():
    return user_login_api(request)
