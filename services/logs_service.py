from bson.json_util import dumps, loads
from database.log import Log
from database.action import Action
from database.properties import ViewProperties, NavigateProperties, ClickProperties
from flask.json import jsonify
from datetime import datetime
from settings import TIME_FORMAT

class _LogService:

    def get_logs(self, userId, from_date, to_date, typesList):

        try:
            if from_date is not None: datetime.strptime(from_date, TIME_FORMAT)
            if to_date is not None: datetime.strptime(to_date, TIME_FORMAT)
        except:
            raise ValueError('INVALID_TIME_FORMAT')
        
        #ignore objectID's and generated _cls from the result. 
        pipeline = [{ "$project": { "_id": 0, "actions.properties._cls": 0 }}]
        match = self._construct_match_array(userId, from_date, to_date, typesList)
        filter = self._construct_filter_array(from_date, to_date, typesList)

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
                            "cond": { "$and" : filter }
                        },
                    },
                    "userId": 1,
                    "sessionId": 1
                }
            })

        # Remove documents that have an empty action array.
        pipeline.append({ "$match": { "actions.0": { "$exists": True } }})
        cursor = Log.objects.aggregate(pipeline)
        return loads(dumps(cursor))

    def add_logs(self, logs):
        if not logs: raise ValueError('NO_LOGS_PROVIDED')
        
        # Run through all received logs. This for-loop does two things
        # - Validates all inputs
        # - Once all is validated, returns an array of actions well constructed by our helper below.
        #
        # This way if any log in the body is invalid, then the entire body doesn't get inserted. Simulating a rollback.
        #
        
        logArray = []

        for log in logs:
            userId = log.get('userId')
            sessionId = log.get('sessionId')
            actions = log.get('actions')
            
            if not userId: raise ValueError('MISSING_USERID')
            if not sessionId: raise ValueError('MISSING_SESSIONID')
            if not actions: raise ValueError('MISSING_ACTIONS')

            actionArray = []
            
            for action in actions:
                actionArray.append(self._createActionModel(action))
            logArray.append({ 'userId': userId, 'sessionId': sessionId, 'actionArray': actionArray})

        # Validation and creation of array objects complete. Insert them all into Log collections
        for _log in logArray:
            Log.objects(
                userId=_log.get('userId'), 
                sessionId=_log.get('sessionId')
            ).update_one(push_all__actions=_log.get('actionArray'), upsert=True)
        
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

    def _construct_filter_array(self, from_date, to_date, typesList):
        filter = []
        if from_date:
            filter.append({ '$gte': [ '$$action.time', from_date ]})
        if to_date:
            filter.append({ '$lte': [ '$$action.time', to_date ]})
        if typesList: 
            filter.append({ '$in' : ['$$action.type', typesList ]})
        return filter


    def _createActionModel(self, action):
        if not action: raise ValueError("EMPTY_ACTION")
        _properties = action.get('properties')
        _type = action.get('type')
        _time = action.get('time')
        if not _time: raise ValueError("MISSING_TIME_VALUE")
        try:
            datetime.strptime(_time,TIME_FORMAT)
        except:
            raise ValueError("INVALID_TIME_FORMAT")

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

