from flask import request, Blueprint
from flask.json import jsonify
from services.logs_service import LogService

logs = Blueprint('logs', __name__)

@logs.route('/')
def get_logs():
    
    userId = request.args.get('userId')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    types = request.args.get('types')

    typesList = []
    if types is not None: typesList = types.split(',')
    return jsonify(LogService.get_logs(userId, from_date, to_date, typesList))

@logs.route('/', methods=['POST'])
def add_log():
    data = request.get_json()

    userId = data.get('userId')
    sessionId = data.get('sessionId')
    actions = data.get('actions') 
    if not userId: return jsonify({ 'code': 'MISSING_USERID'}), 400 
    if not sessionId: return jsonify({ 'code': 'MISSING_SESSIONID'}), 400 
    if not actions: return jsonify({ 'error': 'MISSING_ACTIONS'}), 400 
    LogService.add_log(userId, sessionId, actions)
    return jsonify(data), 200
