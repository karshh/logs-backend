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

class ExampleTest(TestCase):
    def setUp(self):
        disconnect()
        connect('mongoenginetest', host='mongodb://localhost:27017/pytest')
        self.w = TestApp(app)

    def tearDown(self):
       disconnect()

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