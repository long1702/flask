from mongo_connect import DB
if __name__ == '__main__':
    database = DB
    index_name = [("mention_id", -1),("topic_id", -1)]
    #create_index will handle case if that index already exists
    database.mention.create_index(index_name, unique=True)