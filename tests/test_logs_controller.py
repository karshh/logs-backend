import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
from unittest import TestCase
from flask_webtest import TestApp
from app import app
from mongoengine import connect, disconnect
from database.log import Log
from database.action import Action
from database.properties import ClickProperties, ViewProperties, NavigateProperties

class TestLogController(TestCase):
    def setUp(self):
        disconnect()
        connect('mongoenginetest', host='mongodb://localhost:27017/pytest')
        self.w = TestApp(app)

    def tearDown(self):
       disconnect()

    ############################################
    #
    # TESTING GET /logs
    #
    ############################################

    def test_status_code_with_valid_get_request(self):
        r = self.w.get('/logs/?')
        # Assert there was no messages flushed:
        assert r is not None
        assert r.content_type == 'application/json'
        assert r.status_int < 400

    def test_retrieving_valid_log(self):
        answer = [ 
            { 
                'userId': '12345', 
                'sessionId': 'asdfg',
                'actions': [
                    {
                        'type':'CLICK',
                        'properties': {
                            'locationX': 52,
                            'locationY': 22
                        },
                        'time':'2018-10-18T21:37:28-06:00'
                    }
                ]
            }
        ]
        action = Action(_time='2018-10-18T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=52, locationY=22))
        log = Log(userId='12345', sessionId='asdfg', actions=[ action ])
        log.save()

        r = self.w.get('/logs/?')
        log.delete()
        assert r.json == answer


    def test_retrieving_log_by_user(self):
        answer1 = [ 
            { 
                'userId': 'ASDF', 
                'sessionId': '123',
                'actions': [
                    {
                        'type':'CLICK',
                        'properties': {
                            'locationX': 52,
                            'locationY': 22
                        },
                        'time':'2018-10-18T21:37:28-06:00'
                    }
                ]
            }
        ]
        answer2 = [ 
            { 
                'userId': '12345', 
                'sessionId': 'asdfg',
                'actions': [
                    {
                        'type':'CLICK',
                        'properties': {
                            'locationX': 52,
                            'locationY': 22
                        },
                        'time':'2018-10-18T21:37:28-06:00'
                    }
                ]
            }
        ]
        action = Action(_time='2018-10-18T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=52, locationY=22))
        log1 = Log(userId='12345', sessionId='asdfg', actions=[ action ])
        log2 = Log(userId='ASDF', sessionId='123', actions=[ action ])
        log1.save()
        log2.save()

        r1 = self.w.get('/logs/?userId=ASDF')
        assert r1.json == answer1
        r2 = self.w.get('/logs/?userId=12345')
        assert r2.json == answer2
        r2 = self.w.get('/logs/?userId=12')
        assert r2.json == []

        log1.delete()
        log2.delete()

        
    def test_retrieving_log_by_from_to(self):
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

        r1 = self.w.get('/logs/?to=2018-10-19T00:00:00-06:00')
        assert r1.json == answer1
        r2 = self.w.get('/logs/?from=2018-10-19T00:00:00-06:00')
        assert r2.json == answer2
        r3 = self.w.get('/logs/?from=2018-10-18T00:00:00-06:00&to=2018-10-19T00:00:00-06:00')
        assert r3.json == answer3
        r4 = self.w.get('/logs/?from=2019-10-18T00:00:00-06:00&to=2020-10-19T00:00:00-06:00')
        assert r4.json == []

        log1.delete()
        log2.delete()

    def test_retrieving_logs_with_matching_types(self):
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


        r1 = self.w.get('/logs/?types=CLICK')
        assert r1.json == answer1
        r2 = self.w.get('/logs/?types=CLICK,VIEW')
        assert r2.json == answer2
        r3 = self.w.get('/logs/?types=NAVIGATE')
        assert r3.json == answer3
        log1.delete()
        log2.delete()

    def test_retrieving_with_invalid_type(self):
        answer = [
            {
                'userId': '12345',
                'sessionId': 'asdfg',
                'actions': [
                    {
                        'type': 'CLICK',
                        'properties': {
                            'locationX': 52,
                            'locationY': 22
                        },
                        'time': '2018-10-17T21:37:28-06:00'
                    }
                ]
                
            }
        ]
        action1 = Action(_time='2018-10-17T21:37:28-06:00', _type='CLICK', _properties=ClickProperties(locationX=52, locationY=22))
        action2 = Action(_time='2018-10-19T21:37:28-06:00', _type='NAVIGATE', _properties=NavigateProperties(pageFrom='X', pageTo='Y'))
        log = Log(userId='12345', sessionId='asdfg', actions=[ action1, action2 ])
        log.save()

        r1 = self.w.get('/logs/?types=CLICK,WRONGTYPE,VIEW')
        assert r1.status_int == 200
        assert r1.json == answer
        log.delete()


    ############################################
    #
    # TESTING POST /logs
    #
    ############################################

    def test_no_body(self):
        r1 = self.w.post_json('/logs/', { }, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'MISSING_USERID' }

    def test_no_userId(self):
        body = { 
            'sessionId': '12345', 
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'CLICK',
                    'properties': {
                        'locationX': 52,
                        'locationY': 22
                    }
                }
            ]}

        r1 = self.w.post_json('/logs/', body, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'MISSING_USERID' }

    def test_no_sessionId(self):
        body = { 
            'userId': '12345', 
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'CLICK',
                    'properties': {
                        'locationX': 52,
                        'locationY': 22
                    }
                }
            ]}

        r1 = self.w.post_json('/logs/', body, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'MISSING_SESSIONID' }

    def test_no_actions(self):
        body = { 
            'userId': '12345',
            'sessionId': '1234'
            }

        r1 = self.w.post_json('/logs/', body, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'MISSING_ACTIONS' }

    def test_empty_actions(self):
        body = { 
            'userId': '12345',
            'sessionId': '1234',
            'actions': []
            }

        r1 = self.w.post_json('/logs/', body, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'MISSING_ACTIONS' }


    def test_invalid_time(self):
        body = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28',
                    'type': 'CLICK',
                    'properties': {
                        'locationX': 52,
                        'locationY': 22
                    }
                }
            ]}

        r1 = self.w.post_json('/logs/', body, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'INVALID_TIME_FORMAT' }

    def test_invalid_type(self):
        body = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'INVALID',
                    'properties': {
                        'locationX': 52,
                        'locationY': 22
                    }
                }
            ]}

        r1 = self.w.post_json('/logs/', body, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'INVALID_ACTION_TYPE' }


    def test_invalid_type(self):
        body = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'INVALID',
                    'properties': {
                        'locationX': 52,
                        'locationY': 22
                    }
                }
            ]}

        r1 = self.w.post_json('/logs/', body, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'INVALID_ACTION_TYPE' }

    def test_invalid_navigate(self):
        body1 = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'NAVIGATE',
                    'properties': {
                        'pageTo': '22'
                    }
                }
            ]}
        body2 = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'NAVIGATE',
                    'properties': {
                        'pageFrom': '22'
                    }
                }
            ]}

        r1 = self.w.post_json('/logs/', body1, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'MISSING_PAGEFROM_VALUE' }

        r2 = self.w.post_json('/logs/', body2, expect_errors=True)
        assert r2.status_int == 400
        assert r2.json == {'success': False, 'code': 'MISSING_PAGETO_VALUE' }

    def test_invalid_click(self):
        body1 = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'CLICK',
                    'properties': {
                        'locationX': 22
                    }
                }
            ]}
        body2 = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'CLICK',
                    'properties': {
                        'locationY': 23
                    }
                }
            ]}

        r1 = self.w.post_json('/logs/', body1, expect_errors=True)
        assert r1.status_int == 400
        assert r1.json == {'success': False, 'code': 'MISSING_LOCATION_Y_VALUE' }

        r2 = self.w.post_json('/logs/', body2, expect_errors=True)
        assert r2.status_int == 400
        assert r2.json == {'success': False, 'code': 'MISSING_LOCATION_X_VALUE' }
    
    def test_invalid_click(self):
        body = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'time': '2018-10-18T21:37:28-06:00',
                    'type': 'VIEW',
                    'properties': {
                        'asdf': 'asdf'
                    }
                }
            ]}

        r = self.w.post_json('/logs/', body, expect_errors=True)
        assert r.status_int == 400
        assert r.json == {'success': False, 'code': 'MISSING_VIEWEDID_VALUE' }

    def test_missing_time(self):
        body = { 
            'userId': '12345', 
            'sessionId': '1234',
            'actions' : [
                {
                    'type': 'VIEW',
                    'properties': {
                        'asdf': 'asdf'
                    }
                }
            ]}

        r = self.w.post_json('/logs/', body, expect_errors=True)
        assert r.status_int == 400
        assert r.json == {'success': False, 'code': 'MISSING_TIME_VALUE' }
