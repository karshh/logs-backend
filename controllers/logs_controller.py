from flask import request, Blueprint
from flask.json import jsonify
from services.logs_service import get_logs, add_log

logs = Blueprint('logs', __name__)

@logs.route('/')
def GetLogs():
    userId = request.args.get('userId')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    types = request.args.get('types')
    typesList = []
    if types is not None: typesList = types.split(',')
    return jsonify(get_logs(userId, from_date, to_date, typesList))

@logs.route('/', methods=['POST'])
def AddLog():
    data = request.get_json()
    add_log(data)
    return jsonify({ 'success': True }), 200
