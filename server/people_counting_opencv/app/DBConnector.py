from pymongo import MongoClient


class DBConnector:
    def __init__(self, host='localhost', port=27017, db_name="cognitive_portal", collection_name="counting_logs"):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[self.collection_name]
