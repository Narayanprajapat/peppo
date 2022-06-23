import os
from bson import ObjectId
from flask import make_response, jsonify
from werkzeug.utils import secure_filename
from app.api.auth.authentication import token_decode
from app.api.common.aws import upload_to_s3, generate_presign_link
from app.api.models.files_model import File
from datetime import datetime


def upload_file_api(request):
    try:
        file = request.files['file']
        token = request.cookies.get('token')
    except Exception as e:
        return make_response(jsonify({'message': 'Invalid Input', 'status_code': 400}), 400)

    if file == "":
        return make_response(jsonify({'message': 'Invalid Input File'}), 400)

    if token == "":
        return make_response(jsonify({'message': 'You are not authenticate'}), 400)

    token = token_decode(token)
    if not token['user_type'] == 'operation':
        return make_response(jsonify({'message': 'Client user can not upload file', 'status_code': 400}), 400)

    filename = secure_filename(file.filename)
    if not validate_file_extension(filename):
        return make_response(jsonify({'message': 'File Accepted Only {pptx, docx, xlsx}', 'status_code': 400}), 400)

    path = 'app/static/files/'
    file.save(os.path.join(path, filename))
    res = upload_to_s3(path + filename, os.getenv('BUCKET_NAME'), filename)

    if res['status_code'] != 200:
        return make_response(jsonify({'message': 'Internal Server Error', "status_code": 500}), 500)

    payload = {
        "filename": filename,
        "username": token['email'],
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    }
    File().create(payload)
    os.remove(path+filename)
    return make_response(jsonify({'message': 'success', 'status_code': 200}), 200)


def download_file_api(assignment_id, request):
    try:
        token = request.cookies.get('token')
    except Exception as e:
        return make_response(jsonify({'message': 'Invalid Input', 'status_code': 400}), 400)

    if token is None:
        return make_response(jsonify({'message': "Access denied", "status_code": 400}), 400)

    token = token_decode(token)
    if not token['user_type'] != 'operation':
        return make_response(jsonify({'message': 'Access denied', 'status_code': 400}), 400)

    try:
        result = File().read({"_id": ObjectId(assignment_id)}, {"filename": 1, "created_at": 1})
        output = generate_presign_link(os.getenv('BUCKET_NAME'), result['filename'])

        if output['status_code'] != 200:
            return make_response(jsonify({'message': 'Internal Server Error', "status_code": 500}), 500)

        return make_response(jsonify({'message': 'success', 'download-link': output['link']}), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify({'message': 'Internal Server Error', "status_code": 500}), 500)


def list_upload_files_api(request):
    try:
        token = request.cookies.get('token')
    except Exception as e:
        return make_response(jsonify({'message': 'Invalid Input', 'status_code': 400}), 400)

    if token is None:
        return make_response(jsonify({'message': "Please Login", "status_code": 400}), 400)

    token = token_decode(token)
    if not token['user_type'] != 'operation':
        return make_response(jsonify({'message': 'Access denied', 'status_code': 400}), 400)

    try:
        result = File().find()
        files = list()
        for i in list(result):
            files.append({
                'assignment_id': str(i['_id']),
                'filename': i['filename'],
                'upload_time': i['created_at']
            })

        return make_response(jsonify({'message': 'success', 'upload_file': files, 'status_code': 200}), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify({'message': 'Internal Server Error', "status_code": 500}), 500)


def validate_file_extension(filename):
    allowed_file = ['pptx', 'docx', 'xlsx']
    if filename.split(".")[-1].lower() in allowed_file:
        return True
    return False
