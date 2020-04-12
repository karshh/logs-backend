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

    def test_construct_all_fields_not_None(self):
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
    # TESTING LogService._construct_match_array
    #
    ############################################
    def test_construct_match_array_empty(self):
        result = LogService._construct_match_array(None, None, None, None)
        assert result is not None
        assert len(result) == 0

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
        print(result1)
        assert result1 == answer1

        result2 = LogService.get_logs(None, '2018-10-19T00:00:00-06:00', None, None)
        assert result2 is not None
        assert result2 == answer2

        result3 = LogService.get_logs(None, '2018-10-18T00:00:00-06:00', '2018-10-19T00:00:00-06:00', None)
        assert result3 is not None
        assert result3 == answer3
        log1.delete()
        log2.delete()