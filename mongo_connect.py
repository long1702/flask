import os 
import pymongo

def get_database(url, name, port):
    mongo_client = pymongo.MongoClient(host=url, port=port)
    database = mongo_client[str(name)]
    return database

DB_LINK = os.environ.get('DB_LINK')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT', 27017)
DB = get_database(DB_LINK, DB_NAME, int(DB_PORT))
