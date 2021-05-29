import unittest
import mongomock
import crawler
from mock import patch, Mock
from datetime import datetime
from requests import Response

ISODATETIME = '2020-08-14T00:00:00'
DATETIME = datetime.fromisoformat('2020-08-14T00:00:00')
TOPIC_VALUE_SAMPLE = [{
  "topic_id":"t_1",
  "crawl_period":10,
  "next_crawl_at": DATETIME
},
{
  "topic_id":"t_2",
  "crawl_period":10,
  "next_crawl_at": DATETIME
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


AFTER_CRAWL = {
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
  "is_updated": True,
  "true_label": True,
  "created_date": DATETIME
}

GET_SOLR_RESULT = [{
    "id": "456",
    "created_date": ISODATETIME,
    "is_noisy": True,
    "is_ignore": False
}]

AFTER_CRAWL_1 = [{
  "mention_id":"123",
  "mention_type":1,
  "topic_id":"t_1",
  "predict":
  [{
    "label":False,
    "confident_score":0.9,
    "model":"v1",
    "sent_date" : DATETIME
  }],
  "is_updated": True,
  "true_label": True,
  "created_date": DATETIME
},
{
  "mention_id":"456",
  "mention_type":1,
  "topic_id":"t_1",
  "predict":
  [{
    "label":False,
    "confident_score":0.9,
    "model":"v1",
    "sent_date" : DATETIME
  }],
  "is_updated": True,
  "true_label": False,
  "created_date": DATETIME  
}]


GET_SOLR_RESULT_1 = [{
    "id": "456",
    "created_date": ISODATETIME,
},
{
    "id": "123",
    "created_date": ISODATETIME,
    "is_noisy": True,
}]

EXTRACT_DATA = {
  "true":{
    "mention_id": "456",
    "created_date": DATETIME,
    "true_label": True
    },
  "false":{
    "mention_id": "456",
    "created_date": DATETIME,
    "true_label": False
  }
    
}

MENTION_TEST_LIST = ["123","456"]

REQUESTS_REQUEST = {
    "response":{
        "docs": [{
            "id": "123",
            "created_date": DATETIME,
            "is_noisy": True
          },
          {
            "id": "456",
            "created_date": DATETIME,
          }]
    }
}

URL= "http://solrtopic.younetmedia.com/solr/topic_t_1/select"

QUERYSTRING = {
  "fl": "id,is_noisy,is_ignore,created_date",
  "q": "*:*",
  "wt": "json",
  "rows": '10',
  "start": '0',
  "fq": "id:(%s)" % " ".join(MENTION_TEST_LIST)
}

def mocked_requests_request(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[1] == URL:
        return MockResponse(REQUESTS_REQUEST, 200)
    return MockResponse(None, 404)

class Test_Crawler(unittest.TestCase):
    def setUp(self):
        self.database = mongomock.MongoClient().database
        for item in TOPIC_VALUE_SAMPLE:
            self.database.topic.insert_one(item)
        for item in MENTION_VALUE_SAMPLE:
            self.database.mention.insert_one(item)

    def tearDown(self):
        pass
        
    def test_get_mentionid_list(self):
        mentionlist = crawler.get_mentionid_list(self.database.mention,"t_1")
        self.assertEqual(mentionlist,MENTION_TEST_LIST)
    
    @patch('crawler.requests')
    @patch('crawler.SOLR_KEY', 'ABC')
    def test_get_solr_data(self, mock_requests):
        mock_requests.request = Mock(side_effect = mocked_requests_request)
        _ = crawler.get_solr_data(MENTION_TEST_LIST,"t_1",0,10)
        headers = {'authorization': crawler.SOLR_KEY}
        mock_requests.request.assert_called_with("GET", URL, data="", headers=headers, params=QUERYSTRING )

    def test_extract_data_with_ignore_and_noisy(self):
        #is_ignore is False, is_noisy is True
        GET_SOLR_RESULT[0]["is_noisy"] = True
        GET_SOLR_RESULT[0]["is_ignore"] = False
        record = crawler.extract_data(GET_SOLR_RESULT[0])
        self.assertDictEqual(record, EXTRACT_DATA["true"])
        #is_ignore is True, is_noisy is True
        GET_SOLR_RESULT[0]["is_ignore"] = True
        record = crawler.extract_data(GET_SOLR_RESULT[0])
        self.assertDictEqual(record, EXTRACT_DATA["true"])
        #is_ignore is True, is_noisy is False
        GET_SOLR_RESULT[0]["is_noisy"] = False
        record = crawler.extract_data(GET_SOLR_RESULT[0])
        self.assertDictEqual(record, EXTRACT_DATA["true"])
        #is_ignore is False, is_noisy is False
        GET_SOLR_RESULT[0]["is_ignore"] = False
        record = crawler.extract_data(GET_SOLR_RESULT[0])
        self.assertDictEqual(record, EXTRACT_DATA["false"])

    def test_extract_data_missing_ignore_or_noisy(self):
        #is_ignore is missing and is_noisy is true
        GET_SOLR_RESULT[0]["is_noisy"] = True
        GET_SOLR_RESULT[0].pop("is_ignore") 
        record = crawler.extract_data(GET_SOLR_RESULT[0])
        self.assertDictEqual(record, EXTRACT_DATA["true"])
        #is_ignore and is_noisy is missing
        GET_SOLR_RESULT[0].pop("is_noisy") 
        record = crawler.extract_data(GET_SOLR_RESULT[0])
        self.assertDictEqual(record, EXTRACT_DATA["false"])
        #is_noisy is missing and is_ignore is False
        GET_SOLR_RESULT[0]["is_ignore"] = False
        record = crawler.extract_data(GET_SOLR_RESULT[0])
        self.assertDictEqual(record, EXTRACT_DATA["false"])

    @patch('crawler.get_solr_data')
    def test_crawl_with_is_noisy_or_is_ignore(self, mock_get_solr_data):
        mock_get_solr_data.return_value = GET_SOLR_RESULT
        crawler.crawl(self.database, "t_2")
        mention_record = list(self.database.mention.find({"topic_id": "t_2"}, {"_id": 0}))
        self.assertDictEqual(mention_record[0], AFTER_CRAWL)

    @patch('crawler.get_solr_data')
    def test_crawl_with_missing_noisy_ignore(self, mock_get_solr_data):
        mock_get_solr_data.return_value = GET_SOLR_RESULT_1
        crawler.crawl(self.database, "t_1")
        mention_record = list(self.database.mention.find({"topic_id": "t_1"}, {"_id": 0}))
        self.assertListEqual(mention_record, AFTER_CRAWL_1)
      
    

    


