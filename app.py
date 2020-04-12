from flask import Flask, request, Blueprint
from flask.json import jsonify
from db import mongo
from controllers.logs_controller import logs
from settings import MONGO_URL

app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URL
mongo.init_app(app)
app.register_blueprint(logs, url_prefix='/logs')
if __name__ == '__main__':
    app.run()