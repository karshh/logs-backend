from bson.json_util import dumps, loads
from database.log import Log


class _LogService:

    def get_logs(self, userId, from_date, to_date, typesList):

        pipeline = []
        match = []
        filter = []
        
        pipeline.append({ "$project": { "_id": 0 }}) #ignore objectID's from the result. 

        if userId: 
            match.append({ 'userId': userId })
        if from_date: 
            filter.append({ '$gte' : ['$$action.time', from_date ]})
            match.append({ 'actions.time': { '$gte': from_date } })
        if to_date: 
            filter.append({ '$lte' : ['$$action.time', to_date ]})
            match.append({ 'actions.time': { '$lte': to_date } })
        if typesList: 
            filter.append({ '$in' : ['$$action.type', typesList ]})
            match.append({ 'actions.type': {'$in': typesList} })
        if match: 
            pipeline.append( {"$match": { "$and": match } } )
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
        cursor = Log.objects.aggregate(pipeline)
        return loads(dumps(cursor))

    def add_log(self, userId, sessionId, actions):
        inserted_data = Log.objects(userId=userId, sessionId=sessionId).update_one(push_all__actions=actions, upsert=True)
        return inserted_data

LogService = _LogService()

