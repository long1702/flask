import time
import pymongo
import json
import requests
from datetime import datetime
from key import SOLR_KEY


BATCH_SIZE = 200


def extract_data(doc):
    return_val = {}
    return_val["mention_id"] = doc["id"]
    return_val["created_date"] = datetime.fromisoformat(doc["created_date"])

    is_noisy = doc.get('is_noisy', False)
    is_ignore = doc.get('is_ignore', False)
    return_val["true_label"] = is_ignore or is_noisy
    return return_val

def get_solr_data(mention_list, topic_id, start, row):
    q = " ".join(mention_list)
    #print(row) 
    url = "http://solrtopic.younetmedia.com/solr/topic_" + str(topic_id) + "/select"
    #print(topic_id)
    querystring = {}
    querystring["fl"] = "id,is_noisy,is_ignore,created_date"
    querystring["q"] = "*:*"
    querystring["wt"] = "json"
    querystring["rows"] = str(row)
    querystring["start"] = str(start)
    querystring["fq"] = "id:(%s)" % q
    #print(querystring)
    payload = ""
    headers = {'authorization': SOLR_KEY}
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    #print(response.url)
    #print(response.status_code)
    if response.status_code != 200:
        return None
    response_json = response.json()
    #print(response_json)
    response_docs = response_json["response"]["docs"]
    return response_docs

def get_mentionid_list(collection, topic_id):
    mention_ids = []
    #print(collection)
    for ele in collection.find({"topic_id": topic_id, "is_updated": False}, {"mention_id": 1, "_id": 0}) :
        #print(ele)
        mention_ids.append(ele["mention_id"])

    #print(len(mention_ids))
    return mention_ids
    
def crawl(database, topic_id):
    print(topic_id)
    mention_ids = get_mentionid_list(database.mention, topic_id)
    #print(mention_ids)
    num_of_mention = len(mention_ids)
    print(num_of_mention)
    
    if num_of_mention == 0:
        return
    total_batch = num_of_mention // BATCH_SIZE

    for i in range(total_batch + 1):
        sub_mention_list = mention_ids[BATCH_SIZE * i: BATCH_SIZE * (i+1)]
        if (i > 0) and (i % 10 == 0):
            print(i)
        #print(len(sub_mention_list))
        response_docs = get_solr_data(sub_mention_list, topic_id, start=0, row=BATCH_SIZE)
        bulk = database.mention.initialize_unordered_bulk_op()
        #print(response_docs)
        if response_docs is None or response_docs == []:
            continue
        for doc in response_docs:
            record = extract_data(doc)
            keys = {"topic_id": topic_id, "mention_id" : record["mention_id"]}
            bulk.find(keys).update({ "$set": { "is_updated" : True, "true_label": record["true_label"], "created_date" : record["created_date"]}})
        bulk.execute()
