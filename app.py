from flask import Flask
from flask import request
from flask.json import jsonify
from service.logs_service import get_all_logs, get_a_log, add_log
app = Flask(__name__)


@app.route('/logs')
def GetLogs():
    return jsonify(get_all_logs())

@app.route('/logs', methods=['POST'])
def AddLog():
    data = request.get_json()
    add_log(data)
    return jsonify({ 'success': True }), 200


if __name__ == '__main__':
    app.run()