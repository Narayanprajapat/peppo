import ssl
import pymongo
import os

# Mongodb database connection
mongo = pymongo.MongoClient(
    os.environ.get("DATABASE_URL"),
    connect=False,
)
database_name = mongo['EasyArab']


class Authentication:
    def __init__(self):
        self.sort = None
        self.query = None
        self.data = None

    def create(self, data):
        self.data = data
        return database_name.auth.insert_one(self.data)

    def read(self, query, sort):
        self.query = query
        self.sort = sort
        return database_name.auth.find_one(self.query, self.sort)

    def update(self, query, data):
        self.query = query
        self.data = data
        return database_name.auth.update_one(self.query, self.data)
