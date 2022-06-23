from flask import Blueprint, request
from app.api.auth.file import upload_file_api

operation = Blueprint('operation', __name__, static_folder='static', template_folder='templates')


@operation.route('/api/upload_file', methods=['POST'])
def upload_file():
    return upload_file_api(request)

