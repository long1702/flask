import unittest
import json
import mongomock
import datetime
from mock import patch, Mock
from post_end_point import server

DATETIME = datetime.datetime.fromisoformat('2020-08-14T00:00:00')

TEST_SIMPLE_DATA = {
  "items": [{
    "topic": "t_1",
    "mention_type": 1,
    "mention_id": "123",
    "label": "NONE",
    "confident_score": 0.9,
    "model": "v1"
  },
  {
    "topic": "t_2",
    "mention_type": 2,
    "mention_id": "456",
    "label": "JUNK_ADS",
    "confident_score": 0.1,
    "model": "v2"
  }]
}


TOPIC_VALUE_SAMPLE = [{
  "topic_id":"t_1",
  "crawl_period": 86400,
  "next_crawl_at": DATETIME + datetime.timedelta(seconds = 86400)
},
{
  "topic_id":"t_2",
  "crawl_period":86400,
  "next_crawl_at": DATETIME + datetime.timedelta(seconds = 86400)
}]

MENTION_VALUE_SAMPLE = [{
  "mention_id":"123",
  "mention_type":1,
  "topic_id": "t_1",
  "predict":
  [{
    "label":False,
    "confident_score":0.9,
    "model":"v1",
    "sent_date" : DATETIME
  }],
  'is_updated': False
},
{
  "mention_id":"456",
  "mention_type":2,
  "topic_id": "t_2",
  "predict":
  [{
    "label":True,
    "confident_score":0.1,
    "model":"v2",
    "sent_date" : DATETIME
  }],
  'is_updated': False
}]


RESPONSE_DATA = {
  "results": "Operation Succeed"
}



class Test_Post_Service(unittest.TestCase):
    def setUp(self):
        self.client = server.test_client()
        self.mock_get_database_patcher = patch('post_end_point.DB', mongomock.MongoClient().database)
        self.mock_get_database = self.mock_get_database_patcher.start()
        self.mock_datetime_patcher = patch('post_end_point.mongo_utils.datetime')
        self.mock_datetime = self.mock_datetime_patcher.start()
        self.mock_datetime.utcnow = Mock(return_value = DATETIME)

    def send_request(self, record):
        send_data = self.client.post(
            '/spam-data',
            data=json.dumps(record),
            headers={'Content-Type' : 'application/json'}
        )
        return json.loads(send_data.get_data(as_text=True))


    def tearDown(self):
        self.mock_get_database_patcher.stop()
        self.mock_datetime_patcher.stop()
    
    def test_post_request(self):
      '''
      TEST RESPONSE MESSAGE AFTER INSERTING NEW DATA
      '''
      data = self.send_request(TEST_SIMPLE_DATA)
      self.assertEqual(data, RESPONSE_DATA)


    def test_update_post_request(self):
      '''
      TEST RESPONSE MESSAGE AFTER UPDATING DATABASE
      '''
      _ = self.send_request(TEST_SIMPLE_DATA)
      _ = self.send_request(TEST_SIMPLE_DATA)
      data = self.send_request(TEST_SIMPLE_DATA)
      self.assertEqual(data, RESPONSE_DATA)
    
    def test_error_post_request(self):
      '''
      TEST RESPONSE MESSAGE WHEN SENDING WRONG API FORMAT
      '''
      WRONG_API_MESSAGE = {
        "texts": ["t_1", "t_2"]
      }
      WRONG_API_MESSAGE_2 = {
        "items": 
        [{ 
          "topic": "t_1",
          "mention_type": 1,
          "mention_id": "456",
          "label": "NONE",
          "confident_score": 0.9
        }]
      }
      
      ERROR_API_MESSAGE = {
        "error": "'items' field is wrong or missing."
      }

      ERROR_API_MESSAGE_2 ={
        "error": "model field is wrong or missing."
      }

      data = self.send_request(WRONG_API_MESSAGE)
      self.assertEqual(data, ERROR_API_MESSAGE)
      data = self.send_request(WRONG_API_MESSAGE_2)
      self.assertEqual(data, ERROR_API_MESSAGE_2)

    def test_data_insertion(self):
      '''
      TEST DATABASE RESULT
      '''
      _ = self.send_request(TEST_SIMPLE_DATA)
      database = self.mock_get_database
      topic_record = list(database.topic.find({}, {"_id": 0}))
      mention_record = list(database.mention.find({}, {"_id": 0}))
      self.assertListEqual(mention_record, MENTION_VALUE_SAMPLE)
      self.assertListEqual(topic_record, TOPIC_VALUE_SAMPLE)