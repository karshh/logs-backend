import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
import unittest
from mongoengine import connect, disconnect
from database.log import Log
from database.action import Action
from services.logs_service import LogService
from database.properties import ClickProperties, ViewProperties, NavigateProperties
from datetime import datetime


class TestLogService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        disconnect()
        connect('mongoenginetest', host='mongodb://localhost:27017/pytest')

    @classmethod
    def tearDownClass(cls):
       disconnect()

    ############################################
    #
    # TESTING LogService._construct_match_array
    #
    ############################################

    def test_construct_match_array_empty(self):
        result = LogService._construct_match_array(None, None, None, None)
        assert result is not None
        assert len(result) == 0

    def test_construct_match_array_userId(self):
        answer = [ { 'userId': '12345' }]
        result = LogService._construct_match_array('12345', None, None, None)
        assert result is not None
        assert result == answer
        
    def test_construct_match_array_from_time(self):
        answer = [ { 'actions.time': { '$gte': '2018-10-18T21:37:28-06:00' } } ]
        result = LogService._construct_match_array(None, '2018-10-18T21:37:28-06:00', None, None)
        assert result is not None
        assert result == answer

    def test_construct_match_array_to_time(self):
        answer = [ { 'actions.time': { '$lte': '2018-10-18T21:37:28-06:00' } } ]
        result = LogService._construct_match_array(None, None, '2018-10-18T21:37:28-06:00', None)
        assert result is not None
        assert result == answer

    def test_construct_match_array_from_to_time(self):
        answer = [ { 'actions.time': { '$gte': '2017-10-17T21:37:28-06:00' } }, { 'actions.time': { '$lte': '2018-10-17T21:37:28-06:00' } } ]
        result = LogService._construct_match_array(None, '2017-10-17T21:37:28-06:00', '2018-10-17T21:37:28-06:00', None)
        assert result is not None
        assert result == answer

    def test_construct_match_array_userId_from_to_time(self):
        answer = [ { 'userId': '12345' }, { 'actions.time': { '$gte': '2017-10-17T21:37:28-06:00' } }, { 'actions.time': { '$lte': '2018-10-17T21:37:28-06:00' } } ]
        result = LogService._construct_match_array('12345', '2017-10-17T21:37:28-06:00', '2018-10-17T21:37:28-06:00', None)
        assert result is not None
        assert result == answer

    def test_construct_match_types(self):
        answer = [ { 'actions.type': {'$in': ['CLICK', 'VIEW', 'NAVIGATE' ]} } ]
        result = LogService._construct_match_array(None, None, None, ['CLICK', 'VIEW', 'NAVIGATE' ])
        assert result is not None
        assert result == answer

    def test_construct_all_match_fields_not_None(self):
        answer = [ 
            { 'userId': '12345' },
            { 'actions.time': { '$gte': '2017-10-17T21:37:28-06:00' } },
            { 'actions.time': { '$lte': '2018-10-17T21:37:28-06:00' } },
            { 'actions.type': {'$in': ['CLICK', 'VIEW', 'NAVIGATE' ]} } 
            ]
        result = LogService._construct_match_array('12345', '2017-10-17T21:37:28-06:00', '2018-10-17T21:37:28-06:00', ['CLICK', 'VIEW', 'NAVIGATE' ])
        assert result is not None
        assert result == answer


    ############################################
    #
    # TESTING LogService._construct_filter_array
    #
    ############################################

    def test_construct_filter_array_empty(self):
        result = LogService._construct_filter_array(None, None, None)
        assert result is not None
        assert len(result) == 0

    def test_construct_filter_array_from_time(self):
        answer = [ { '$gte': [ '$$action.time', '2018-10-18T21:37:28-06:00' ]} ]
        result = LogService._construct_filter_array('2018-10-18T21:37:28-06:00', None, None)
        assert result is not None
        assert result == answer

    def test_construct_filter_array_to_time(self):
        answer = [ { '$lte': [ '$$action.time', '2018-10-18T21:37:28-06:00' ]}  ]
        result = LogService._construct_filter_array(None,'2018-10-18T21:37:28-06:00', None)
        assert result is not None
        assert result == answer

    def test_construct_filter_array_from_to_time(self):
        answer = [ { '$gte': [ '$$action.time', '2017-10-18T21:37:28-06:00' ]}, { '$lte': [ '$$action.time', '2018-10-18T21:37:28-06:00' ]} ]
        result = LogService._construct_filter_array('2017-10-18T21:37:28-06:00', '2018-10-18T21:37:28-06:00', None)
        assert result is not None
        assert result == answer

    def test_construct_filter_array_from_to_time(self):
        answer = [ { '$in' : ['$$action.type', ['CLICK', 'VIEW'] ]} ]
        result = LogService._construct_filter_array(None, None, ['CLICK', 'VIEW'])
        assert result is not None
        assert result == answer

    def test_construct_all_filter_fields_not_None(self):
        answer = [ 
            { '$gte': [ '$$action.time', '2017-10-18T21:37:28-06:00' ]}, 
            { '$lte': [ '$$action.time', '2018-10-18T21:37:28-06:00' ]},
            { '$in' : ['$$action.type', ['CLICK', 'VIEW', 'NAVIGATE'] ]}  
            ]
        result = LogService._construct_filter_array('2017-10-18T21:37:28-06:00', '2018-10-18T21:37:28-06:00', ['CLICK', 'VIEW', 'NAVIGATE' ])
        assert result is not None
        assert result == answer

    ############################################
    #
    # TESTING LogService._create_action_model
    #
    ############################################
    def test_empty_input(self):
        try:
            LogService._createActionModel(None)
            assert False
        except ValueError as e:
            assert str(e) == "EMPTY_ACTION"

    def test_invalid_time_format(self):
        try:
            LogService._createActionModel({ "time": "2012-02-01", "type": "VIEW", "properties": { "viewedId": "12345" } })
            assert False
        except ValueError as e:
            assert str(e) == "INVALID_TIME_FORMAT"
    def test_invalid_type_input(self):
        try:
            LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "VIEWS", "properties": { "viewedId": "12345" } })
            assert False
        except ValueError as e:
            assert str(e) == "INVALID_ACTION_TYPE"

    def test_view_with_missing_viewId(self):
        try:
            LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "locationX": 12345 } })
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_VIEWEDID_VALUE"
            
    def test_navigate_with_missing_pageFrom(self):
        try:
            LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "NAVIGATE", "properties": { "pageTo": "X" } })
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_PAGEFROM_VALUE"
            
    def test_navigate_with_missing_pageTo(self):
        try:
            LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "NAVIGATE", "properties": { "pageFrom": "X" } })
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_PAGETO_VALUE"
            
    def test_click_with_missing_locationX(self):
        try:
            LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "CLICK", "properties": { "locationY": 1234 } })
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_LOCATION_X_VALUE"
            
    def test_click_with_missing_locationY(self):
        try:
            LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "CLICK", "properties": { "locationX": 1234 } })
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_LOCATION_Y_VALUE"
            
    def test_create_valid_click(self):
        try:
            answer = Action(_time="2018-10-20T21:37:28-06:00", _type="CLICK", _properties=ClickProperties(locationX=23, locationY=1234))
            result = LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "CLICK", "properties": { "locationX": 23, "locationY": 1234 } })
            
            assert result is not None
            assert answer == result
        except ValueError as e:
            assert False
            
    def test_create_valid_navigate(self):
        try:
            answer = Action(_time="2018-10-20T21:37:28-06:00", _type="NAVIGATE", _properties=NavigateProperties(pageFrom='X', pageTo='Y'))
            result = LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "NAVIGATE", "properties": { "pageFrom": "X", "pageTo": "Y" } })
            assert result is not None
            assert answer == result
        except ValueError as e:
            assert False

    def test_create_valid_view(self):
        try:
            answer = Action(_time="2018-10-20T21:37:28-06:00", _type="VIEW", _properties=ViewProperties(viewedId='12345'))
            result = LogService._createActionModel({ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } })
            assert result is not None
            assert answer == result
        except ValueError as e:
            assert False
            

    ############################################
    #
    # TESTING LogService.get_logs
    #
    ############################################
    def test_empty_logs(self):
        result = LogService.get_logs(None, None, None, None)
        assert len(result) == 0

    def test_logs_with_an_existing_log(self):
        answer = [{ 
            'userId': '12345', 
            'sessionId': 'asdfg', 
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'CLICK',
                    'properties': {
                        'locationX': 52,
                        'locationY': 22
                    }
                }
            ]}]
        action = Action(_time='2018-10-18T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=52, locationY=22))
        log = Log(userId='12345', sessionId='asdfg', actions=[ action ])
        log.save()

        result = LogService.get_logs(None, None, None, None)
        assert result is not None
        assert result == answer
        log.delete()

    def test_logs_with_an_matching_log_userId(self):
        answer = [{ 
            "userId": "12345", 
            "sessionId": "asdfg", 
            "actions" : [
                {
                    "time": "2018-10-18T21:37:28-06:00",
                    "properties": {
                        "locationX": 52,
                        "locationY": 22
                    },
                    "type": "CLICK",
                },
                {
                    "time": "2018-10-20T21:37:28-06:00",
                    "properties": {
                        "pageFrom": "X",
                        "pageTo": "Y"
                    },
                    "type": "NAVIGATE"
                }
            ]}]
        action1 = Action(_time='2018-10-18T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=52, locationY=22))
        action2 = Action(_time='2018-10-20T21:37:28-06:00', _type='NAVIGATE', _properties=NavigateProperties(pageFrom='X', pageTo='Y'))
        log = Log(userId='12345', sessionId='asdfg', actions=[ action1, action2 ])
        log.save()

        result1 = LogService.get_logs('12345', None, None, None)
        assert result1 is not None
        assert result1 == answer
        result2 = LogService.get_logs('asdf', None, None, None)
        assert result2 is not None
        assert len(result2) == 0
        log.delete()

    def test_logs_with_an_matching_types(self):
        answer1 = [{ 
            "userId": "12345", 
            "sessionId": "asdfg", 
            "actions" : [
                {
                    "time": "2018-10-20T21:37:28-06:00",
                    "properties": {
                        "locationX": 52,
                        "locationY": 22
                    },
                    "type": "CLICK"
                }
            ]},{
            "userId": "ASDFG", 
            "sessionId": "12345", 
            "actions" : [
                {
                    "time": "2019-10-20T21:37:28-06:00",
                    "properties": {
                        "locationX": 60,
                        "locationY": 30
                    },
                    "type": "CLICK"
                }
            ]},
            ]

        answer2 = [{ 
            "userId": "12345", 
            "sessionId": "asdfg", 
            "actions" : [
                {
                    "time": "2018-10-20T21:37:28-06:00",
                    "properties": {
                        "locationX": 52,
                        "locationY": 22
                    },
                    "type": "CLICK"
                }
            ]},{
            "userId": "ASDFG", 
            "sessionId": "12345", 
            "actions" : [
                {
                    "time": "2019-10-19T21:37:28-06:00",
                    "properties": {
                        "viewedId": "12345",
                    },
                    "type": "VIEW"
                },
                {
                    "time": "2019-10-20T21:37:28-06:00",
                    "properties": {
                        "locationX": 60,
                        "locationY": 30
                    },
                    "type": "CLICK"
                }
            ]},
            ]
        answer3 = [{ 
            "userId": "12345", 
            "sessionId": "asdfg", 
            "actions" : [
                {
                    "time": "2018-10-20T21:37:28-06:00",
                    "properties": {
                        "pageFrom": "X",
                        "pageTo": "Y"
                    },
                    "type": "NAVIGATE"
                }
            ]}
            ]
            
        action1 = Action(_time='2018-10-20T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=52, locationY=22))
        action2 = Action(_time='2018-10-20T21:37:28-06:00', _type='NAVIGATE', _properties=NavigateProperties(pageFrom='X', pageTo='Y'))
        log1 = Log(userId='12345', sessionId='asdfg', actions=[ action1, action2 ])
        action3 = Action(_time='2019-10-19T21:37:28-06:00', _type='VIEW', _properties=ViewProperties(viewedId='12345'))
        action4 = Action(_time='2019-10-20T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=60, locationY=30))
        log2 = Log(userId='ASDFG', sessionId='12345', actions=[ action3, action4 ])
        log1.save()
        log2.save()

        result1 = LogService.get_logs(None, None, None, ['CLICK'])
        assert result1 is not None
        assert result1 == answer1
        result2 = LogService.get_logs(None, None, None, ['CLICK', 'VIEW'])
        assert result2 is not None
        assert result2 == answer2
        result3 = LogService.get_logs(None, None, None, ['NAVIGATE'])
        assert result3 is not None
        assert result3 == answer3
        log1.delete()
        log2.delete()

    def test_logs_with_a_from_and_to(self):
        answer1 = [{ 
            "userId": "12345", 
            "sessionId": "asdfg", 
            "actions" : [
                {
                    "time": "2018-10-17T21:37:28-06:00",
                    "properties": {
                        "locationX": 52,
                        "locationY": 22
                    },
                    "type": "CLICK"
                }
            ]},{
            "userId": "ASDFG", 
            "sessionId": "12345", 
            "actions" : [
                {
                    "time": "2018-10-18T21:37:28-06:00",
                    "properties": {
                        "viewedId": "12345"
                    },
                    "type": "VIEW"
                }
            ]},
            ]

        answer2 = [{ 
            "userId": "12345", 
            "sessionId": "asdfg", 
            "actions" : [
                {
                    "time": "2018-10-19T21:37:28-06:00",
                    "properties": {
                        "pageFrom": 'X',
                        "pageTo": 'Y'
                    },
                    "type": "NAVIGATE"
                }
            ]},{
            "userId": "ASDFG", 
            "sessionId": "12345", 
            "actions" : [
                {
                    "time": "2018-10-20T21:37:28-06:00",
                    "properties": {
                        "locationX": 60,
                        "locationY": 30
                    },
                    "type": "CLICK"
                }
            ]},
            ]
        answer3 = [{
            "userId": "ASDFG", 
            "sessionId": "12345", 
            "actions" : [
                {
                    "time": "2018-10-18T21:37:28-06:00",
                    "properties": {
                        "viewedId": "12345",
                    },
                    "type": "VIEW"
                }
            ]}]
            
        action1 = Action(_time='2018-10-17T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=52, locationY=22))
        action2 = Action(_time='2018-10-19T21:37:28-06:00', _type='NAVIGATE', _properties=NavigateProperties(pageFrom='X', pageTo='Y'))
        log1 = Log(userId='12345', sessionId='asdfg', actions=[ action1, action2 ])
        action3 = Action(_time='2018-10-18T21:37:28-06:00', _type='VIEW', _properties=ViewProperties(viewedId='12345'))
        action4 = Action(_time='2018-10-20T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=60, locationY=30))
        log2 = Log(userId='ASDFG', sessionId='12345', actions=[ action3, action4 ])
        log1.save()
        log2.save()
        result1 = LogService.get_logs(None, None, '2018-10-19T00:00:00-06:00', None)
        assert result1 is not None
        assert result1 == answer1

        result2 = LogService.get_logs(None, '2018-10-19T00:00:00-06:00', None, None)
        assert result2 is not None
        assert result2 == answer2

        result3 = LogService.get_logs(None, '2018-10-18T00:00:00-06:00', '2018-10-19T00:00:00-06:00', None)
        assert result3 is not None
        assert result3 == answer3
        log1.delete()
        log2.delete()

    ############################################
    #
    # TESTING LogService.add_log
    #
    ############################################
    def test_add_none(self):
        try:
            result = LogService.add_log(None, None, None)
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_USERID"

    def test_miss_userId(self):
        try:
            result = LogService.add_log(None, "12345", [{ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } }])
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_USERID"

    def test_miss_sessionId(self):
        try:
            result = LogService.add_log("1234", None, [{ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } }])
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_SESSIONID"

    def test_miss_action(self):
        try:
            result = LogService.add_log("1234", "12345", [])
            assert False
        except ValueError as e:
            assert str(e) == "MISSING_ACTIONS"


    def test_result_success(self):
            result = LogService.add_log("1234", "12345",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } }])
            assert result is not None
            assert result.get('success') is True
            Log.objects().delete()

    def test_add_valid_action(self):
            action = Action(_type="VIEW", _properties=ViewProperties(viewedId="12345"), _time="2018-10-20T21:37:28-06:00")
            result = LogService.add_log("1234", "12345",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } }])
            
            logs = Log.objects(userId="1234")
            assert logs is not None
            assert len(logs) == 1
            assert logs[0].userId == "1234"
            assert logs[0].sessionId == "12345"
            assert logs[0].actions == [ action ]
            Log.objects().delete()

    def test_add_valid_action_non_upserted(self):
            action1 = Action(_type="VIEW", _properties=ViewProperties(viewedId="12345"), _time="2018-10-20T21:37:28-06:00")
            action2 = Action(_type="NAVIGATE", _properties=NavigateProperties(pageFrom="X", pageTo="Y"), _time="2018-10-20T21:37:28-06:00")
            result = LogService.add_log("1234", "12345",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } }])
            result = LogService.add_log("12345", "ASDF",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "NAVIGATE", "properties": { "pageFrom": "X", "pageTo": "Y" } }])
            
            logs = Log.objects()
            assert logs is not None
            assert len(logs) == 2
            assert logs[0].userId == "1234"
            assert logs[0].sessionId == "12345"
            assert logs[0].actions == [ action1 ]

            assert logs[1].userId == "12345"
            assert logs[1].sessionId == "ASDF"
            assert logs[1].actions == [ action2 ]
            Log.objects().delete()

    def test_add_valid_action_upserted(self):
            action1 = Action(_type="VIEW", _properties=ViewProperties(viewedId="12345"), _time="2018-10-20T21:37:28-06:00")
            action2 = Action(_type="NAVIGATE", _properties=NavigateProperties(pageFrom="X", pageTo="Y"), _time="2018-10-20T21:37:28-06:00")
            result = LogService.add_log("1234", "12345",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } }])
            result = LogService.add_log("1234", "12345",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "NAVIGATE", "properties": { "pageFrom": "X", "pageTo": "Y" } }])
            
            logs = Log.objects()
            assert logs is not None
            assert len(logs) == 1
            assert logs[0].userId == "1234"
            assert logs[0].sessionId == "12345"
            assert logs[0].actions == [ action1, action2 ]
            Log.objects().delete()

    def test_add_valid_action_non_upserted_different_session(self):
            action1 = Action(_type="VIEW", _properties=ViewProperties(viewedId="12345"), _time="2018-10-20T21:37:28-06:00")
            action2 = Action(_type="NAVIGATE", _properties=NavigateProperties(pageFrom="X", pageTo="Y"), _time="2018-10-20T21:37:28-06:00")
            result = LogService.add_log("1234", "12345",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "VIEW", "properties": { "viewedId": "12345" } }])
            result = LogService.add_log("1234", "ASDF",  [{ "time": "2018-10-20T21:37:28-06:00", "type": "NAVIGATE", "properties": { "pageFrom": "X", "pageTo": "Y" } }])
            
            logs = Log.objects()
            assert logs is not None
            assert len(logs) == 2
            assert logs[0].userId == "1234"
            assert logs[0].sessionId == "12345"
            assert logs[0].actions == [ action1 ]

            assert logs[1].userId == "1234"
            assert logs[1].sessionId == "ASDF"
            assert logs[1].actions == [ action2 ]
            Log.objects().delete()

    ############################################
    #
    # TESTING LogService.add_logs
    #
    ############################################
    def test_add_no_log(self):
        try:
            result = LogService.add_logs(None)
            assert False
        except Exception as e:
            assert str(e) == "NO_LOGS_PROVIDED"

    def test_add_empty_log(self):
        try:
            result = LogService.add_logs([])
            assert False
        except Exception as e:
            assert str(e) == "NO_LOGS_PROVIDED"

    def test_add_valid_log(self):
        Log.objects().delete()

        body = [{
            "userId": "ABC123XYZ",
            "sessionId": "XYZ456ABC",
            "actions": [
                {
                "time": "2018-10-18T21:37:28-06:00",
                "type": "CLICK",
                "properties": {
                    "locationX": 52,
                    "locationY": 11
                }
                },
                {
                "time": "2018-10-18T21:37:30-06:00",
                "type": "VIEW",
                "properties": {
                    "viewedId": "FDJKLHSLD"
                }
                },
                {
                "time": "2018-10-18T21:37:30-06:00",
                "type": "NAVIGATE",
                "properties": {
                    "pageFrom": "communities",
                    "pageTo": "inventory"
                }
                }
            ]
        },
        { 
            "userId": "asd", 
            "sessionId": "asdfg", 
            "actions" : [
                {
                    "time": "2018-10-18T21:37:28-06:00",
                    "type": "CLICK",
                    "properties": {
                        "locationX": 60,
                        "locationY": 70
                    }
                },
                {
                    "time": "2018-10-20T21:37:28-06:00",
                    "type": "NAVIGATE",
                    "properties": {
                        "pageFrom": "X",
                        "pageTo": "Y"
                    }
                }
            ]
        }]
        result = LogService.add_logs(body)
        assert result == { 'success': True }
        log = Log.objects()
        assert log is not None
        assert len(log) == 2

        assert log[0].userId == 'ABC123XYZ'
        assert log[0].sessionId == 'XYZ456ABC'
        actions = log[0].actions
        assert actions is not None
        assert len(actions) == 3
        assert actions[0] == Action(_time="2018-10-18T21:37:28-06:00", _type="CLICK", _properties=ClickProperties(locationX=52, locationY=11))
        assert actions[1] == Action(_time="2018-10-18T21:37:30-06:00", _type="VIEW", _properties=ViewProperties(viewedId="FDJKLHSLD"))
        assert actions[2] == Action(_time="2018-10-18T21:37:30-06:00", _type="NAVIGATE", _properties=NavigateProperties(pageFrom="communities", pageTo="inventory"))
        
        assert log[1].userId == 'asd'
        assert log[1].sessionId == 'asdfg'
        actions = log[1].actions
        assert actions is not None
        assert len(actions) == 2
        assert actions[0] == Action(_time="2018-10-18T21:37:28-06:00", _type="CLICK", _properties=ClickProperties(locationX=60, locationY=70))
        assert actions[1] == Action(_time="2018-10-20T21:37:28-06:00", _type="NAVIGATE", _properties=NavigateProperties(pageFrom="X", pageTo="Y")) 
        
        Log.objects().delete()
