from db import mongo
from bson.json_util import dumps, loads

def get_logs(userId, from_date, to_date, typesList):
    print(userId, from_date, to_date, typesList)

    pipeline = []
    match = []
    filter = []
    
    pipeline.append({ "$project": { "_id": 0 }})
    if userId: match.append({ 'userId': userId })
    if from_date: 
        filter.append({ '$gte' : ['$$action.time', from_date ]})
        match.append({ 'actions.time': { '$gte': from_date } })
    if to_date: 
        filter.append({ '$lte' : ['$$action.time', to_date ]})
        match.append({ 'actions.time': { '$lte': to_date } })
    if typesList: 
        filter.append({ '$in' : ['$$action.type', typesList ]})
        match.append({ 'actions.type': {'$in': typesList} })
    if match: pipeline.append( {"$match": { "$and": match } } )
    if filter: 
        pipeline.append({ 
            "$project": 
            {
                "actions": 
                {
                    "$filter": 
                    {
                        "input": "$actions",
                        "as": "action",
                        "cond":{"$and": filter }
                    }
                },
                "userId": 1,
                "sessionId": 1
            }
        })
    cursor = mongo.db.logs.aggregate(pipeline)
    return loads(dumps(cursor))

def add_log(data):
    inserted_data = mongo.db.logs.insert(data)
    return inserted_data
