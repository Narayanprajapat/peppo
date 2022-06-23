import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jwt
from datetime import datetime, timedelta
from flask import make_response, jsonify
import random
import os
import hashlib
from app.api.models.authentication_model import Authentication
from dotenv import load_dotenv

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
        full_name = request.form['full_name']
        email = request.form['email']
        user_type = request.form['user_type']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
    except Exception as e:
        print(e)
        return make_response(jsonify({"message": "Invalid Input", "status_code": 400}), 400)

    if full_name == "":
        return make_response(jsonify({'message': 'Invalid Input Fullname'}), 400)
    if email == "":
        return make_response(jsonify({'message': 'Invalid Input Email'}), 400)
    if user_type == "":
        return make_response(jsonify({'message': 'Invalid Input User Type'}), 400)
    if password == "":
        return make_response(jsonify({'message': 'Invalid Input Password'}), 400)
    if confirm_password == "":
        return make_response(jsonify({'message': 'Invalid Input Confirm Password'}), 400)




    if not user_type.lower() in ['operation', 'client']:
        return make_response(jsonify({"message": "User type must be client or operation user", "status_code": 400}),
                             400)

    try:
        # email validation
        if email.find('@') == -1 or email.find('.') == -1:
            return make_response(jsonify({'message': 'Email Is Invalid', "status_code": 400}), 400)

        # password validation
        if password != confirm_password:
            return make_response(jsonify({'message': 'Password Mismatch', "status_code": 400}), 400)

        # validating user with database.
        query = {"email": email}
        resp = Authentication().read(query, {})
        print(resp)
        if resp is not None:
            return make_response(jsonify({'message': 'User Already Exist', "status_code": 400}), 400)

        # hashing password.
        password = hash_password(password)
        confirm_password = hash_password(confirm_password)

        otp = random.randint(100000, 999999)
        payload = {
            'email': email,
            'full_name': full_name,
            'password': password,
            'confirm_password': confirm_password,
            'user_type': user_type.lower(),
            'otp': otp,
            'email_verify': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }
        Authentication().create(payload)
        otp_sender(email, full_name, otp, "Account Verification Code")
        return make_response(jsonify({'message': 'success', "status_code": 200}), 200)
    except Exception as e:
        print('{}'.format(e))
        return make_response(jsonify({'message': 'Internal Server Error', "status_code": 500}), 500)


def account_verification_api(request):
    try:
        email = request.form['email']
        otp = request.form['otp']
    except Exception as e:
        return make_response(jsonify({"message": "Invalid Input", "status_code": 400}), 400)

    if email == "":
        return make_response(jsonify({'message': 'Invalid Input Email'}), 400)

    if otp == "":
        return make_response(jsonify({'message': 'Invalid Input Otp'}), 400)

    try:
        query = {"email": email}
        sort = {"otp": 1}
        resp = Authentication().read(query, sort)

        if resp is None:
            return make_response(jsonify({'message': 'User Not Exist', "status_code": 400}), 400)

        if resp['otp'] == int(otp):
            Authentication().update(query, {"$set": {"email_verify": True, "updated_at": datetime.now()}})
            return make_response(jsonify({"message": "success", "validate": "otp is valid", "status_code": 200}), 200)

        return make_response(jsonify({"validate": "otp is not valid", "status": 400}), 400)
    except Exception as e:
        return make_response(jsonify({'message': 'Internal Server Error', "status_code": 500}), 500)


def otp_sender(receiver_email, name, otp, subject):
    sender_email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    message = MIMEMultipart("alternative")
    text = """

        Hello {}

        Your Account Verification OTP  :  {}
        
    """.format(name, str(otp), receiver_email, str(otp))
    print(text)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    part1 = MIMEText(text, "plain")
    message.attach(part1)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
            return True
    except Exception as e:
        print(e)
        return False


def user_login_api(request):
    try:
        email = request.form['email']
        password = request.form['password']
    except Exception as e:
        return make_response(jsonify({'message': 'Invalid Input'}), 400)

    if email == "":
        return make_response(jsonify({'message': 'Invalid Input Email'}), 400)

    if password == "":
        return make_response(jsonify({'message': 'Invalid Input Password'}), 400)

    try:
        query = {"email": email}
        sort = {"password": 1, "user_type": 1, "email_verify": 1}
        resp = Authentication().read(query, sort)

        if not resp['email_verify']:
            return make_response(jsonify({"message": "Please Verify Your Account", "status_code": 400}), 400)

        if resp['password'] == hash_password(password):
            token_input = {
                'email': email,
                'user_type': resp['user_type'],
                'expiration': str(datetime.utcnow() + timedelta(days=30)),
            }
            token = token_encode(token_input)
            if token is None:
                return make_response(jsonify({"message": "Token Generation Failed.", "status_code": 500}), 500)

            if resp['user_type'] == "operation":
                redirect_url = '/api/upload_file'
            else:
                redirect_url = ['/api/list/upload_file', 'api/download_file/<assignment_id>']

            response = make_response(jsonify({
                "message": "Login successful",
                "token": token,
                'redirect_url': redirect_url
            }), 200)
            response.set_cookie('token', token)
            return response
        return make_response(jsonify({"message": "Unable to verify password", "status_code": 403}), 403)
    except Exception as e:
        return make_response(jsonify({'message': 'Internal Server Error', "status_code": 500}), 500)
