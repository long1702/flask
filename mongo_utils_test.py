import unittest
import json
import mongomock
import datetime
from mock import patch, Mock
from mongo_utils import MongoUtils

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
  "crawl_period":10,
  "next_crawl_at": (DATETIME + datetime.timedelta(seconds = 10))
},
{
  "topic_id":"t_2",
  "crawl_period":10,
  "next_crawl_at": (DATETIME + datetime.timedelta(seconds = 10))
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

MENTION_UPDATE_DATA_SAMPLE = [{
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
}]

TEST_UPDATE_PREDICT_DATA = {
  "items": [{
    "topic": "t_1",
    "mention_type": 1,
    "mention_id": "123",
    "label": "NONE",
    "confident_score": 0.9,
    "model": "v1"
  }]
}

MENTION_UPDATE_PREDICT_DATA_SAMPLE = [{
    "label":False,
    "confident_score":0.9,
    "model":"v1",
    "sent_date" : DATETIME
},
{
    "label":False,
    "confident_score":0.9,
    "model":"v1",
    "sent_date" : DATETIME
}]



class Test_MongoUtils(unittest.TestCase):
    def setUp(self):
        self.database = mongomock.MongoClient().database
        self.mock_datetime_patcher = patch('mongo_utils.datetime')
        self.mock_datetime = self.mock_datetime_patcher.start()
        self.mock_datetime.utcnow = Mock(return_value = DATETIME)
        for item in TEST_SIMPLE_DATA["items"]:
            test_mongo_util = MongoUtils(self.database, item, 10)
            test_mongo_util.to_database() 

    def tearDown(self):
        self.mock_datetime_patcher.stop()

    def test_insert_new_record(self):
        self.maxDiff = None
        mention_record = list(self.database.mention.find({}, {"_id": 0}))
        topic_record = list(self.database.topic.find({}, {"_id": 0}))
        self.assertListEqual(topic_record, TOPIC_VALUE_SAMPLE)
        self.assertListEqual(mention_record, MENTION_VALUE_SAMPLE)

    def test_check_missing_attribute(self):
        MODEL_MISSING = { 
            "topic": "t_1",
            "mention_type": 1,
            "mention_id": "123",
            "label": "NONE",
            "confident_score": 0.9
        }
        test_mongo_util = MongoUtils(self.database, MODEL_MISSING,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "model")

        TOPIC_MISSING = { 
            "mention_type": 1,
            "mention_id": "123",
            "label": "NONE",
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, TOPIC_MISSING,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "topic")

        MENTION_TYPE_MISSING = { 
            "topic": "t_1",
            "mention_id": "123",
            "label": "NONE",
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, MENTION_TYPE_MISSING,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "mention_type")

        MENTION_ID_MISSING = { 
            "topic": "t_1",
            "mention_type": 1,
            "label": "NONE",
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, MENTION_ID_MISSING,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "mention_id")

        LABEL_MISSING = { 
            "topic": "t_1",
            "mention_type": 1,
            "mention_id": "123",
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, LABEL_MISSING,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "label")

        CONFIDENT_SCORE_MISSING = { 
            "topic": "t_1",
            "mention_type": 1,
            "mention_id": "123",
            "label": "NONE",
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, CONFIDENT_SCORE_MISSING,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "confident_score")

    def test_check_wrong_type_attribute(self):
        MODEL_WRONG_TYPE = { 
            "topic": "t_1",
            "mention_type": 1,
            "mention_id": "123",
            "label": "NONE",
            "confident_score": 0.9,
            "model": 1
        }
        test_mongo_util = MongoUtils(self.database, MODEL_WRONG_TYPE,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "model")

        TOPIC_WRONG_TYPE = { 
            "topic": True,
            "mention_type": 1,
            "mention_id": "123",
            "label": "NONE",
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, TOPIC_WRONG_TYPE,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "topic")

        MENTION_TYPE_WRONG = { 
            "topic": "t_1",
            "mention_type": "abc",
            "mention_id": "123",
            "label": "NONE",
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, MENTION_TYPE_WRONG,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "mention_type")

        MENTION_ID_WRONG_TYPE = { 
            "topic": "t_1",
            "mention_type": 1,
            "mention_id": 1,
            "label": "NONE",
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, MENTION_ID_WRONG_TYPE,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "mention_id")

        LABEL_WRONG_TYPE = { 
            "topic": "t_1",
            "mention_type": 1,
            "mention_id": "123",
            "label": 1,
            "confident_score": 0.9,
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, LABEL_WRONG_TYPE,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "label")

        CONFIDENT_SCORE_WRONG_TYPE = { 
            "topic": "t_1",
            "mention_type": 1,
            "mention_id": "123",
            "label": "NONE",
            "confident_score": "1",
            "model": "v1"
        }

        test_mongo_util = MongoUtils(self.database, CONFIDENT_SCORE_WRONG_TYPE,10)
        self.assertEqual(test_mongo_util.check_type_attribute(), "confident_score")

    def test_update_record(self):
        self.maxDiff =None
        test_mongo_util = MongoUtils(self.database, TEST_UPDATE_DATA["items"][0],10)
        test_mongo_util.to_database() 
        mention_record = list(self.database.mention.find({"topic_id": "t_1"}, {"_id": 0}))
        self.assertListEqual(mention_record, MENTION_UPDATE_DATA_SAMPLE)

    def test_update_crawl_period(self):
        test_mongo_util = MongoUtils(self.database, TEST_UPDATE_DATA["items"][0],10)
        test_mongo_util.update_crawl_period(20)
        topic_record = list(self.database.topic.find({"topic_id": TEST_UPDATE_DATA["items"][0]["topic"]}, {"_id": 0}))
        self.assertEqual(topic_record[0]["crawl_period"],20)

    def test_update_crawl_time_point(self):
        test_mongo_util = MongoUtils(self.database, TEST_UPDATE_DATA["items"][0],10)
        test_mongo_util.update_crawl_time_point('2020-08-14T00:00:00')
        topic_record = list(self.database.topic.find({"topic_id": TEST_UPDATE_DATA["items"][0]["topic"]}, {"_id": 0, "next_crawl_at": 1}))
        self.assertEqual(topic_record[0]["next_crawl_at"],'2020-08-14T00:00:00')

    def test_update_predict(self):
        test_mongo_util = MongoUtils(self.database, TEST_UPDATE_PREDICT_DATA["items"][0],10)
        test_mongo_util.to_database() 
        mention_record = list(self.database.mention.find({"topic_id": "t_1", "mention_id": "123"}, {"_id": 0}))
        self.assertListEqual(mention_record[0]["predict"], MENTION_UPDATE_PREDICT_DATA_SAMPLE)

    def test_record_form(self):
        test_mongo_util = MongoUtils(self.database, TEST_UPDATE_DATA["items"][0],10)
        record = test_mongo_util.record_form(test_mongo_util.predict_form())
        self.assertDictEqual(record,MENTION_UPDATE_DATA_SAMPLE[1])

    def test_predict_form(self):
        test_mongo_util = MongoUtils(self.database, TEST_UPDATE_PREDICT_DATA["items"][0],10)
        predict = test_mongo_util.predict_form()
        self.assertDictEqual(predict,MENTION_UPDATE_PREDICT_DATA_SAMPLE[1])