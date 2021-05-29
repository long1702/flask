from datetime import datetime, timedelta
class MongoUtils:
    def __init__(self, database, record, crawl_period = 0):
        self.topic_collection = database["topic"]
        self.mention_collection = database["mention"]
        self.crawl_period = crawl_period
        self.topic = record.get("topic", None)
        self.mention_type = record.get("mention_type", None)
        self.mention_id = record.get("mention_id", None)
        self.label = record.get("label",None)
        self.confident_score = record.get("confident_score", None)
        self.model = record.get("model", None)
        
    def insert_new_record(self, record, crawl_period):
        keys = {"topic_id": self.topic}
        next_crawl_at= (datetime.utcnow() + timedelta(seconds = crawl_period))
        self.topic_collection.update_one(keys, {"$set": {"crawl_period": crawl_period, "next_crawl_at": next_crawl_at}}, upsert=True)
        self.mention_collection.insert_one(record)

    def update_crawl_period(self, crawl_period):
        keys = {"topic_id": self.topic}
        self.topic_collection.update_one(keys, {"$set": {"crawl_period": crawl_period}})

    def update_crawl_time_point(self, crawl_time_point):
        keys = {"topic_id": self.topic}
        self.topic_collection.update_one(keys, {"$set": {"next_crawl_at": crawl_time_point}}) 
        
    def update_record(self, record):
        self.mention_collection.insert_one(record)

    def update_predict(self, predict):
        keys = {"topic_id": self.topic, "mention_id": self.mention_id}
        self.mention_collection.update_one(keys, {"$push": {"predict" : predict}})

    def mention_check(self):
        keys = {"topic_id": self.topic, "mention_id": self.mention_id}
        num_of_exist = self.mention_collection.count_documents(keys)
        return True if num_of_exist > 0 else False

    def topic_check(self):
        keys = {"topic_id": self.topic}
        num_of_exist = self.topic_collection.count_documents(keys)
        return True if num_of_exist > 0 else False

    def predict_form(self):
        predict = {}
        if self.label == "NONE":
            predict["label"] = False
        else:
            predict["label"] = True
        predict["confident_score"] = self.confident_score
        predict["model"] = self.model
        predict["sent_date"] = datetime.utcnow()
        return predict

    def record_form(self, predict):
        record = {}
        record["mention_id"] = self.mention_id
        record["mention_type"] = self.mention_type
        record["topic_id"] = self.topic
        record["predict"] = [predict]
        record["is_updated"] = False
        return record
    
    def check_type_attribute(self):
        if type(self.topic) not in [str, int]:
            return 'topic'
        elif type(self.mention_type) is not int:
            return 'mention_type'
        elif type(self.mention_id) is not str:
            return 'mention_id'
        elif type(self.label) is not str:
            return 'label'
        elif type(self.confident_score) not in [int, float]:
            return 'confident_score'
        elif type(self.model) is not str:
            return 'model'
        else:
            return None

    def to_database(self):
        predict = self.predict_form()
        if self.mention_check():
            self.update_predict(predict)
            return

        record = self.record_form(predict)
        # Update data to database
        if not self.topic_check():
            self.insert_new_record(record, self.crawl_period)
        else:
            self.update_record(record)
