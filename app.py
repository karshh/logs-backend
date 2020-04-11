from flask import Flask
from flask import request
from flask.json import jsonify
app = Flask(__name__)


@app.route('/', methods = [ 'POST' ])
def hello():
    data = request.get_json()
    return jsonify(data)

if __name__ == '__main__':
    app.run()