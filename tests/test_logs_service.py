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

    def test_construct_match_array_empty(self):
        result = LogService._construct_match_array(None, None, None, None)
        assert result is not None
        assert len(result) == 0



    def test_empty_logs(self):
        result = LogService.get_logs(None, None, None, None)
        assert len(result) == 0



