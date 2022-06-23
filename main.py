# Import Modules
from flask import Flask
from flask_cors import CORS
import os
# Import Route Functions
from app.api.routes.authentication_route import authentication
from app.api.routes.operation_route import operation
from app.api.routes.client_route import client

# Define App
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

# Import Rest API Routes
app.register_blueprint(authentication)
app.register_blueprint(operation)
app.register_blueprint(client)


# Run complete application
if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug='false', host='0.0.0.0', port='5001')
