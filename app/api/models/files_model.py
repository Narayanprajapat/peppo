from app.api.models.authentication_model import database_name


class File:
    def __init__(self):
        self.sort = None
        self.query = None
        self.data = None

    def create(self, data):
        self.data = data
        return database_name.upload_file.insert_one(self.data)

    def read(self, query, sort):
        self.query = query
        self.sort = sort
        return database_name.upload_file.find_one(self.query, self.sort)

    def find(self):
        return database_name.upload_file.find({})
