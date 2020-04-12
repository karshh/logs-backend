from db import mongo
from bson.json_util import dumps, loads

def get_logs(userId, from_date, to_date, typesList):
    print(userId, from_date, to_date, typesList)

    pipeline = []
    match = []
    
    pipeline.append({ "$project": { "_id": 0 }})
    if userId: match.append({ 'userId': userId })
    if typesList: 
        pipeline.append({ 
            "$project": 
            {
                "actions": 
                {
                    "$filter": 
                    {
                        "input": "$actions",
                        "as": "action",
                        "cond":{"$in": ['$$action.type', typesList ]}
                    }
                },
                "userId": 1,
                "sessionId": 1
            }
        })
        match.append({ 'actions.type': {'$in': typesList} })
    if match: pipeline.append( {"$match": { "$and": match } } )
    cursor = mongo.db.logs.aggregate(pipeline)
    return loads(dumps(cursor))

def add_log(data):
    inserted_data = mongo.db.logs.insert(data)
    return inserted_data
