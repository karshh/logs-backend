from db import mongo
from bson.json_util import dumps, loads

def get_logs(userId, from_date, to_date, _type):
    print(userId, from_date, to_date, _type)
    #TODO: Implement querying the logs.
    q = {}
    if userId is not None: q['userId'] = userId
    if from_date is not None or to_date is not None:
        q['actions.time'] = {}
        if from_date is not None: q['actions.time']['$gte'] = from_date
        if to_date is not None: q['actions.time']['$lte'] = from_date
    if _type is not None: q['actions.type'] = _type
    print(q)
    cursor = mongo.db.logs.find(q, { '_id': False })

    return loads(dumps(cursor))

def add_log(data):
    inserted_data = mongo.db.logs.insert(data)
    return inserted_data
