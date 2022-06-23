from flask import Blueprint, request
from app.api.auth.file import download_file_api, list_upload_files_api

client = Blueprint('client', __name__, static_folder='static', template_folder='templates')


@client.route('/api/download_file/<assignment_id>', methods=['GET'])
def download_file(assignment_id):
    return download_file_api(assignment_id, request)


@client.route('/api/list/upload_file', methods=['GET'])
def list_upload_files():
    return list_upload_files_api(request)
