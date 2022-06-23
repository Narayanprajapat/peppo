import jwt
from datetime import datetime, timedelta
import random
import os
import hashlib
from dotenv import load_dotenv

from app.api.common.reponse_maker import response_maker
from app.api.models.auth_models.authentication_model import Authentication
from app.api.models.auth_models.name_model import Name
from app.api.models.auth_models.mobile_model import Mobile
from app.api.models.auth_models.address_model import Address
from app.api.common.mail_sender import otp_sender

load_dotenv()


def token_encode(data):
    try:
        token = jwt.encode(data, os.environ.get('SECRET_KEY'), algorithm="HS256")
        return token
    except Exception as e:
        return None


def token_decode(token):
    try:
        data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
        return data
    except Exception as e:
        return None


def hash_password(value):
    message = value.encode('utf-8')
    hashed_password = hashlib.sha256(message).hexdigest()
    return hashed_password


def user_registered_api(request):
    try:
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
    except Exception as e:
        print(e)
        return response_maker({"message": "Invalid Input", "status_code": 400}, 400)

    if email == "":
        return response_maker({'message': 'Invalid Input Email'}, 400)
    if password == "":
        return response_maker({'message': 'Invalid Input Password'}, 400)
    if confirm_password == "":
        return response_maker({'message': 'Invalid Input Confirm Password'}, 400)

    try:
        # email validation
        if email.find('@') == -1 or email.find('.') == -1:
            return response_maker({'message': 'Email Is Invalid', "status_code": 400}, 400)

        # password validation
        if password != confirm_password:
            return response_maker({'message': 'Password Mismatch', "status_code": 400}, 400)

        # validating user with database.
        query = {"email": email}
        resp = Authentication().read(query, {})

        if resp is not None:
            return response_maker({'message': 'User Already Exist', "status_code": 400}, 400)

        # hashing password.
        password = hash_password(password)

        # otp generator
        otp = random.randint(100000, 999999)

        # payload
        payload = {
            'email': email,
            'password': password,
            'otp': otp,
            'email_verify': False,
            'profile': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }
        Authentication().create(payload)
        otp_sender(email, email, otp, "Account Verification Code")
        return response_maker({'message': 'success', "status_code": 200}, 200)
    except Exception as e:
        print('{}'.format(e))
        return response_maker({'message': 'Internal Server Error', "status_code": 500}, 500)


def user_account_verification_api(request):
    try:
        email = request.form['email']
        otp = request.form['otp']
    except Exception as e:
        return response_maker({"message": "Invalid Input", "status_code": 400}, 400)

    if email == "":
        return response_maker({'message': 'Invalid Input Email'}, 400)

    if otp == "":
        return response_maker({'message': 'Invalid Input Otp'}, 400)

    try:
        query = {"email": email}
        sort = {"otp": 1}
        resp = Authentication().read(query, sort)

        if resp is None:
            return response_maker({'message': 'User Not Exist', "status_code": 400}, 400)

        if resp['otp'] == int(otp):
            Authentication().update(query, {"$set": {"email_verify": True, "updated_at": datetime.now()}})
            token_input = {
                'email': email,
                'expiration': str(datetime.utcnow() + timedelta(days=30)),
            }
            token = token_encode(token_input)
            if token is None:
                return response_maker({"message": "Token Generation Failed.", "status_code": 500}, 500)

            redirect_url = '/api/user/profile'
            response = response_maker({
                "message": "Login successful",
                "token": token,
                'redirect_url': redirect_url
            }, 200)
            response.set_cookie('token', token)
            return response
        return response_maker({"validate": "otp is not valid", "status": 400}, 400)
    except Exception as e:
        print(e)
        return response_maker({'message': 'Internal Server Error', "status_code": 500}, 500)


def user_login_api(request):
    try:
        email = request.form['email']
        password = request.form['password']
    except Exception as e:
        return response_maker({'message': 'Invalid Input'}, 400)

    if email == "":
        return response_maker({'message': 'Invalid Input Email'}, 400)

    if password == "":
        return response_maker({'message': 'Invalid Input Password'}, 400)

    try:
        query = {"email": email}
        sort = {"password": 1, "email_verify": 1}
        resp = Authentication().read(query, sort)

        if not resp['email_verify']:
            return response_maker({"message": "Please Verify Your Account", "status_code": 400}, 400)

        if resp['password'] == hash_password(password):
            token_input = {
                'email': email,
                'expiration': str(datetime.utcnow() + timedelta(days=30)),
            }
            token = token_encode(token_input)
            if token is None:
                return response_maker({"message": "Token Generation Failed.", "status_code": 500}, 500)

            redirect_url = '/api/user/profile'
            response = response_maker({
                "message": "Login successful",
                "token": token,
                'redirect_url': redirect_url
            }, 200)
            response.set_cookie('token', token)
            return response
        return response_maker({"message": "Unable to verify password", "status_code": 403}, 403)
    except Exception as e:
        return response_maker({'message': 'Internal Server Error', "status_code": 500}, 500)


def user_profile_api(request):
    try:
        token = request.cookies.get('token')
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        country_code = request.form['country_code']
        mobile = request.form['mobile']
        address = request.form['address']
        landmark = request.form['landmark']
        city = request.form['city']
        district = request.form['district']
        state = request.form['state']
        pincode = request.form['pincode']
        country = request.form['country']
    except Exception as e:
        print(e)
        return response_maker({"message": "Invalid Input", "status_code": 400}, 400)

    if token == '' or token is None:
        return response_maker({'message': 'Unauthorized User', 'status_code': 401}, 401)

    if firstname == "":
        return response_maker({'message': 'Invalid Input First Name'}, 400)
    if mobile == "":
        return response_maker({'message': 'Invalid Input Mobile No.'}, 400)
    if country_code == "":
        return response_maker({'message': 'Invalid Input Country Code'}, 400)
    if address == "":
        return response_maker({'message': 'Invalid Input Address'}, 400)
    if landmark == "":
        return response_maker({'message': 'Invalid Input Landmark'}, 400)
    if city == "":
        return response_maker({'message': 'Invalid Input City'}, 400)
    if district == "":
        return response_maker({'message': 'Invalid Input District'}, 400)
    if state == "":
        return response_maker({'message': 'Invalid Input State'}, 400)
    if pincode == "":
        return response_maker({'message': 'Invalid Input Pincode'}, 400)
    if country == "":
        return response_maker({'message': 'Invalid Input Country'}, 400)

    try:
        token = token_decode(token)

        query = {"email": token['email']}
        sort = {"_id": 1, "email_verify": 1}

        user_id = Authentication().read(query, sort)
        if not user_id['email_verify']:
            return response_maker({"message": "Access is forbidden to the requested page."}, 403)

        user_id = str(user_id['_id'])

        name_payload = {
            "user_id": user_id,
            "name": {
                "firstname": firstname,
                "lastname": lastname,
            },
            "created_at": datetime.now(),
        }

        mobile_payload = {
            "user_id": user_id,
            "mobile": {
                "country_code": country_code,
                "mobile": mobile,
            },
            "created_at": datetime.now(),
        }

        address_payload = {
            "user_id": user_id,
            "address": {
                "address": address,
                "landmark": landmark,
                "city": city,
                "district": district,
                "pincode": pincode,
                "state": state,
                "country": country
            },
            "created_at": datetime.now(),
        }

        user_id_query = {"user_id": user_id}

        if Mobile().read(user_id_query, {}) is None:
            Mobile().create(mobile_payload)

        if Name().read(user_id_query, {}) is None:
            Name().create(name_payload)

        if Address().read(user_id_query, {}) is None:
            Address().create(address_payload)

        Authentication().update(query, {"$set": {"profile": True}})
        return response_maker({'message': 'success', 'status_code': 200}, 200)
    except Exception as e:
        print(e)
        return response_maker({'message': 'Internal Server Error'}, 500)


def user_forgot_password_api(request):
    try:
        email = request.form['email']
    except Exception as e:
        print(e)
        return response_maker({"message": "Invalid Input", "status_code": 400}, 400)

    if email == "":
        return response_maker({'message': 'Invalid Input Email'}, 400)

    try:
        # email validation
        if email.find('@') == -1 or email.find('.') == -1:
            return response_maker({'message': 'Email Is Invalid', "status_code": 400}, 400)

        # validating user with database.
        query = {"email": email}
        resp = Authentication().read(query, {})

        if resp is None:
            return response_maker({'message': 'User Not Exist', "status_code": 400}, 400)

        # otp generator
        otp = random.randint(100000, 999999)

        # payload
        payload = {
            "$set": {
                'otp': otp,
                'updated_at': datetime.now(),
            }
        }
        Authentication().update(query, payload)
        otp_sender(email, email, otp, "Forgot Password Verification Code")
        return response_maker({'message': 'success', "status_code": 200}, 200)
    except Exception as e:
        print('{}'.format(e))
        return response_maker({'message': 'Internal Server Error', "status_code": 500}, 500)

