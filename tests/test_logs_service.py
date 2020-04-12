import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
import unittest
from mongoengine import connect, disconnect
from database.log import Log
from database.action import Action
from services.logs_service import LogService


class TestLogService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
       disconnect()

    def test_empty_logs(self):
        result = LogService.get_logs(None, None, None, None)
        assert len(result) == 0

    def test_get_logs_with_no_parameters(self):
        log = Log(userId='12345', sessionId='asdfg', actions=[Action(_time="time",_type="type", _properties={ 'locationX': 52, 'locationY': 22 })])
        log.save()

        result = LogService.get_logs(None, None, None, None)
        assert result is not None
        assert len(result) > 0


