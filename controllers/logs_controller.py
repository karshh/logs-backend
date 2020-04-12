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

    result = LogService.get_logs(userId, from_date, to_date, typesList)
    return jsonify(result)

@logs.route('/', methods=['POST'])
def add_log():
    data = request.get_json()

    userId = data.get('userId')
    sessionId = data.get('sessionId')
    actions = data.get('actions') 
    
    try:
        result = LogService.add_log(userId, sessionId, actions)
    except ValueError as e:
            return {'success': False, 'code': str(e) }, 400
    return jsonify(result), 200
