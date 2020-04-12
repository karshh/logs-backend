from bson.json_util import dumps, loads
from database.log import Log
from database.action import Action
from database.properties import ViewProperties, NavigateProperties, ClickProperties
from flask.json import jsonify

class _LogService:

    def get_logs(self, userId, from_date, to_date, typesList):
        
        #ignore objectID's and generated _cls from the result. 
        pipeline = [{ "$project": { "_id": 0, "actions.properties._cls": 0 }}]
        match = self._construct_match_array(userId, from_date, to_date, typesList)

        if match: 
            pipeline.append( {"$match": { "$and": match } } )
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
                            "cond":{ '$in' : ['$$action.type', typesList ]}
                        },
                    },
                    "userId": 1,
                    "sessionId": 1
                }
            })
        cursor = Log.objects.aggregate(pipeline)
        return loads(dumps(cursor))

    def add_log(self, userId, sessionId, actions):

        if not userId: raise ValueError('MISSING_USERID')
        if not sessionId: raise ValueError('MISSING_SESSIONID')
        if not actions: raise ValueError('MISSING_ACTIONS')

        actionArray = []
        actionArray = map(self._createActionModel, actions)

        inserted_data = Log.objects(userId=userId, sessionId=sessionId).update_one(push_all__actions=actionArray, upsert=True)
        return { 'success': True }

    ####################################
    #
    # PRIVATE HELPERS
    #
    ###################################

    def _construct_match_array(self, userId, from_date, to_date, typesList):
        match = []
        if userId: 
            match.append({ 'userId': userId })
        if from_date: 
            match.append({ 'actions.time': { '$gte': from_date } })
        if to_date: 
            match.append({ 'actions.time': { '$lte': to_date } })
        if typesList: 
            match.append({ 'actions.type': {'$in': typesList} })
        return match

    def _createActionModel(self, action):
        _properties = action.get('properties')
        _type = action.get('type')
        _time = action.get('time')
        propertiesModel = None
        if _type == 'CLICK':
            if not _properties.get('locationX'): raise ValueError("MISSING_LOCATION_X_VALUE")
            if not _properties.get('locationY'): raise ValueError("MISSING_LOCATION_Y_VALUE")
            propertiesModel=ClickProperties(locationX = _properties.get('locationX'), locationY = _properties.get('locationY'))
        elif _type == 'VIEW':
            if not _properties.get('viewedId'): raise ValueError("MISSING_VIEWEDID_VALUE")
            propertiesModel=ViewProperties(viewedId = _properties.get('viewedId'))
        elif _type == 'NAVIGATE':
            if not _properties.get('pageFrom') : raise ValueError("MISSING_PAGEFROM_VALUE")
            if not _properties.get('pageTo'): raise ValueError("MISSING_PAGETO_VALUE")
            propertiesModel=NavigateProperties(pageFrom=_properties.get('pageFrom'), pageTo=_properties.get('pageTo'))
        else:
            raise ValueError("INVALID_ACTION_TYPE")

        return Action(_properties=propertiesModel, _time = _time, _type=_type)

LogService = _LogService()

