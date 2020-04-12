from flask import Flask, request, Blueprint
from flask.json import jsonify
from controllers.logs_controller import logs
from settings import MONGO_URL
from database.db import initialize_db

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': MONGO_URL,
    'connect': False,
}
initialize_db(app)

app.register_blueprint(logs, url_prefix='/logs')
if __name__ == '__main__':
    app.run()