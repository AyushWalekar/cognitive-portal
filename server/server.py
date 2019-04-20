from flask import Flask, jsonify
from flask_cors import CORS
from .people_counting_opencv import queries

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)

# sanity check route
# @app.route('/', methods=['POST'])


if __name__ == '__main__':
    app.run()