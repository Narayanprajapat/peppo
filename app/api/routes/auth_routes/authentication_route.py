from flask import Blueprint, request

from app.api.auth.authentication import user_registered_api, user_account_verification_api, user_login_api, \
    user_profile_api

authentication = Blueprint('authentication', __name__, static_folder='static', template_folder='templates')


@authentication.route('/api/user/registered', methods=['POST'])
def user_registered():
    return user_registered_api(request)


@authentication.route('/api/user/account/verification', methods=['POST'])
def account_verification():
    return user_account_verification_api(request)


@authentication.route('/api/user/login', methods=['POST'])
def user_login():
    return user_login_api(request)


@authentication.route('/api/user/profile', methods=['POST'])
def user_profile():
    return user_profile_api(request)