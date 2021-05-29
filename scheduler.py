import time
import pymongo
import json
import requests
from queue import Queue
from datetime import datetime, timedelta
from key import SOLR_KEY
from mongo_connect import DB
from crawler import crawl


INTERVAL = 86400

def crawl_all(database):
    for x in database.topic.find({}, {"topic_id": 1, "next_crawl_at": 1, "crawl_period": 1, "_id": 0}):
        if datetime.utcnow() > x["next_crawl_at"]:
            crawl(database, x["topic_id"])
            next_crawl_at = x["next_crawl_at"] + timedelta(seconds=x["crawl_period"])
            database.topic.update_one({"topic_id": x["topic_id"]}, {"$set": {"next_crawl_at": next_crawl_at}})

if __name__ == "__main__":
    while 1:
        start = time.time()
        print("Start Crawling")
        try:
            crawl_all(DB)
        except KeyboardInterrupt:
            pass
        end = time.time()
        print(end - start)
        print("Finish Crawling")
        if (end - start) < INTERVAL:
            time.sleep(INTERVAL - (end - start))
