import json
import unittest
from mock import patch
from urllib.request import Request, urlopen
from datetime import datetime, timedelta
from mongo_connect import DB
from mongo_utils import MongoUtils

DATETIME = datetime.utcnow()
ISODATETIME = DATETIME

TOPIC_VALUE_SAMPLE = [{
  "topic_id":"t_1",
  "crawl_period":86400
}]

MENTION_VALUE_SAMPLE = [{
    "mention_id":"123",
    "mention_type":1,
    "topic_id": "t_1",
    "predict":
    [{
      "label":False,
      "confident_score":0.9,
      "model":"v1"
    }],
    'is_updated': False
},
{
    "mention_id":"456",
    "mention_type":1,
    "topic_id": "t_1",
    "predict":
    [{
      "label":False,
      "confident_score":0.9,
      "model":"v1"
    }],
    'is_updated': False
}]

TEST_SIMPLE_DATA = {
  "items": [{
    "topic": "t_1",
    "mention_type": 1,
    "mention_id": "123",
    "label": "NONE",
    "confident_score": 0.9,
    "model": "v1"
  }]
}
TEST_UPDATE_DATA = {
  "items": [{
    "topic": "t_1",
    "mention_type": 1,
    "mention_id": "456",
    "label": "NONE",
    "confident_score": 0.9,
    "model": "v1"
  }]
}
TEST_CRAWL_PERIOD_UPDATE = {
  "topic_id": "t_1",
  "new_crawl_period": 20
}

TEST_CRAWL_TIMEPOINT_UPDATE = {
  "topic_id": "t_1",
  "new_time_point": '2020-08-14T00:00:00'
}

RESPONSE_DATA = {
  "results": "Operation Succeed"
}
MENTION_UPDATE_PREDICT_DATA_SAMPLE = [{
    "label":False,
    "confident_score":0.9,
    "model":"v1"
},
{
    "label":False,
    "confident_score":0.9,
    "model":"v1"
}]
class TestRestResponses(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        DB.mention.delete_many({"topic_id": "t_1"})
        DB.topic.delete_many({"topic_id": "t_1"})
        
    def get_response(self, data, path='/spam-data', method='POST'):
        req = Request('http://localhost:4000' + path, method=method)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        json_data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Length', len(json_data))
        response = urlopen(req, json_data)
        return json.loads(response.read())

    def test_database_storage(self):
        _ = self.get_response(TEST_SIMPLE_DATA)
        mention_record = list(DB.mention.find({"topic_id": "t_1"}, {"predict.sent_date": 0, "_id": 0}))
        topic_record = list(DB.topic.find({"topic_id": "t_1"}, {"next_crawl_at": 0,"_id": 0}))
        self.assertEqual(mention_record[0], MENTION_VALUE_SAMPLE[0])
        self.assertDictEqual(topic_record[0], TOPIC_VALUE_SAMPLE[0])

    def test_update_data(self):
        _ = self.get_response(TEST_SIMPLE_DATA)
        _ = self.get_response(TEST_UPDATE_DATA)
        mention_record = list(DB.mention.find({"topic_id": "t_1"}, {"predict.sent_date": 0, "_id": 0}))
        self.assertListEqual(mention_record, MENTION_VALUE_SAMPLE)

    def test_update_data_predict(self):
        _ = self.get_response(TEST_SIMPLE_DATA)
        _ = self.get_response(TEST_SIMPLE_DATA)
        mention_record = list(DB.mention.find({"topic_id": "t_1", "mention_id": "123"}, {"predict.sent_date": 0, "_id": 0}))
        self.assertListEqual(mention_record[0]["predict"], MENTION_UPDATE_PREDICT_DATA_SAMPLE)

        
    
        