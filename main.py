# Import Modules
from flask import Flask
from flask_cors import CORS
# Import Route Functions
from app.api.routes.auth_routes.authentication_route import authentication

# Define App
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

# Import Rest API Routes
app.register_blueprint(authentication)


# Run complete application
if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug='false', host='0.0.0.0', port='5000')
