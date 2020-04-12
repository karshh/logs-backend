from db import mongo
from bson.json_util import dumps
from bson.json_util import loads

def get_all_logs():
    #TODO: Implement querying the logs.
    cursor = mongo.db.logs.find({}, { '_id': False })
    return loads(dumps(cursor))

def add_log(data):
    inserted_data = mongo.db.logs.insert(data)
    return inserted_data
