import unittest
import json
import mongomock
import datetime
from mock import patch, Mock
from update_crawl_attribute import check_crawl_timepoint, check_crawl_period, update_crawl_time_handler, update_crawl_period_handler

RESPONSE_DATA = {
  "results": "Operation Succeed"
}

class Test_Update_Attribute(unittest.TestCase):
    def setUp(self):
        self.mock_get_database_patcher = patch('update_crawl_attribute.DB', mongomock.MongoClient().database)
        self.mock_get_database = self.mock_get_database_patcher.start()

    def tearDown(self):
        self.mock_get_database_patcher.stop()

    def test_crawl_period_check(self):

        TEST_CRAWL_PERIOD_CHECK_1 = {
            "new_crawl_period": 20
        }

        TEST_CRAWL_PERIOD_CHECK_2 = {
            "new_crawl_period": "20"
        } 

        TEST_CRAWL_PERIOD_CHECK_3 = {
            "new_crawl_period": -1
        }

        TEST_CRAWL_TIMEPOINT_CHECK_1 = {
            "new_time_point": 20
        }

        data = check_crawl_period(TEST_CRAWL_PERIOD_CHECK_1)
        self.assertIsNone(data)

        data = check_crawl_period(TEST_CRAWL_PERIOD_CHECK_2)
        self.assertEqual(data, "Data format of new_crawl_period")

        data = check_crawl_period(TEST_CRAWL_PERIOD_CHECK_3)
        self.assertEqual(data, "Data format of new_crawl_period")

        data = check_crawl_period(TEST_CRAWL_TIMEPOINT_CHECK_1)
        self.assertEqual(str(data), "'new_crawl_period'")

    def test_crawl_timepoint_check(self):
        TEST_CRAWL_TIMEPOINT_CHECK_1 = {
            "new_time_point": 20
        }

        TEST_CRAWL_TIMEPOINT_CHECK_2 = {
            "new_time_point": "2020-08-14T00:00:00"
        }

        TEST_CRAWL_PERIOD_CHECK_1 = {
            "new_crawl_period": 20
        }

        data = check_crawl_timepoint(TEST_CRAWL_TIMEPOINT_CHECK_1)
        self.assertEqual(data, "Data format of new_time_point")

        data = check_crawl_timepoint(TEST_CRAWL_TIMEPOINT_CHECK_2)
        self.assertIsNone(data)

        data = check_crawl_timepoint(TEST_CRAWL_PERIOD_CHECK_1)
        self.assertEqual(str(data), "'new_time_point'")
    
    def test_update_crawl_period(self):
        '''
        TEST RESPONSE MESSAGE AFTER CRAWL PERIOD UPDATE
        '''
        TEST_CRAWL_PERIOD_UPDATE = {
          "topic_id": "t_1",
          "new_crawl_period": 20
        }

        data = update_crawl_period_handler(self.mock_get_database, TEST_CRAWL_PERIOD_UPDATE)
        self.assertEqual(data, RESPONSE_DATA)

    def test_update_crawl_timepoint(self):
        '''
        TEST RESPONSE MESSAGE AFTER CRAWL TIMEPOINT UPDATE
        '''

        TEST_CRAWL_TIMEPOINT_UPDATE = {
          "topic_id": "t_1",
          "new_time_point": '2020-08-14T00:00:00'
        }

        data = update_crawl_time_handler(self.mock_get_database, TEST_CRAWL_TIMEPOINT_UPDATE)
        self.assertEqual(data, RESPONSE_DATA)

    def test_update_crawl_period_fail(self):
        '''
        TEST RESPONSE MESSAGE AFTER SENDING WRONG API
        '''
        TEST_CRAWL_TIMEPOINT_UPDATE = {
          "topic_id": "t_1",
          "new_time_point": '2020-08-14T00:00:00'
        }

        TEST_CRAWL_PERIOD_UPDATE_ERROR = {
          "topic_id": "t_1",
          "new_crawl_period": "0"
        }

        UPDATE_CRAWL_PERIOD_FAIL_RESPONSE_1 = {
          "error" : "'new_crawl_period' field is wrong or missing."
        }

        UPDATE_CRAWL_PERIOD_FAIL_RESPONSE_2 = {
          "error" : "Data format of new_crawl_period field is wrong or missing."
        }

        data = update_crawl_period_handler(self.mock_get_database, TEST_CRAWL_TIMEPOINT_UPDATE)
        self.assertEqual(data, UPDATE_CRAWL_PERIOD_FAIL_RESPONSE_1)
        data = update_crawl_period_handler(self.mock_get_database, TEST_CRAWL_PERIOD_UPDATE_ERROR)
        self.assertEqual(data, UPDATE_CRAWL_PERIOD_FAIL_RESPONSE_2)

    def test_update_crawl_timepoint_fail(self):
        '''
        TEST RESPONSE MESSAGE AFTER SENDING WRONG API
        '''
        TEST_CRAWL_PERIOD_UPDATE = {
          "topic_id": "t_1",
          "new_crawl_period": 20
        }

        TEST_CRAWL_TIMEPOINT_UPDATE_ERROR_1 = {
          "topic_id": "t_1",
          "new_crawl_period": '2020-08-14T00:00:00'
        }

        TEST_CRAWL_TIMEPOINT_UPDATE_ERROR_2 = {
          "topic_id": "t_1",
          "new_time_point": '2020 08 14'
        }
        
        UPDATE_CRAWL_TIMEPOINT_FAIL_RESPONSE_1 = {
          "error" : "'new_time_point' field is wrong or missing."
        }

        UPDATE_CRAWL_TIMEPOINT_FAIL_RESPONSE_2 = {
          "error" : "Data format of new_time_point field is wrong or missing."
        } 
        data = update_crawl_time_handler(self.mock_get_database, TEST_CRAWL_PERIOD_UPDATE)
        self.assertEqual(data, UPDATE_CRAWL_TIMEPOINT_FAIL_RESPONSE_1)
        data = update_crawl_time_handler(self.mock_get_database, TEST_CRAWL_TIMEPOINT_UPDATE_ERROR_1)
        self.assertEqual(data, UPDATE_CRAWL_TIMEPOINT_FAIL_RESPONSE_1)
        data = update_crawl_time_handler(self.mock_get_database, TEST_CRAWL_TIMEPOINT_UPDATE_ERROR_2)
        self.assertEqual(data, UPDATE_CRAWL_TIMEPOINT_FAIL_RESPONSE_2)