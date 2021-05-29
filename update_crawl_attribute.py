import mongo_utils 
import datetime
from mongo_connect import DB
from post_end_point import response_form
 
def check_crawl_period(data):
    er = None
    try:
        if (type(data["new_crawl_period"]) is not int) or (data["new_crawl_period"] <= 0):
            er = "Data format of new_crawl_period"
    except KeyError as error:
        er = error 
    return er

def check_crawl_timepoint(data):
    er = None
    try:
        datetime.datetime.fromisoformat(data["new_time_point"])
    except ValueError:
        er = "Data format of new_time_point"
    except KeyError as error:
        er = error
    except TypeError:
        er = "Data format of new_time_point"
    return er

def update_crawl_period_handler(database, data_handle):
    er = check_crawl_period(data_handle)
    if er:
        return response_form(er)

    try:
        item = {
            "topic": data_handle["topic_id"]
        }
        mongo_util = mongo_utils.MongoUtils(database, item) 
        mongo_util.update_crawl_period(data_handle["new_crawl_period"])
    except KeyError as error:
        er = error
    return response_form(er)


def update_crawl_time_handler(database, data_handle):
    er = check_crawl_timepoint(data_handle)
    if er:
        return response_form(er)

    try:
        item = {
            "topic": data_handle["topic_id"]
        }
        mongo_util = mongo_utils.MongoUtils(database, item) 
        mongo_util.update_crawl_time_point(datetime.datetime.fromisoformat(data_handle["new_time_point"]))
    except KeyError as error:
        er = error
        
    return response_form(er)