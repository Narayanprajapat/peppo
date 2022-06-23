from app.api.models.auth_models.authentication_model import database_name


class Mobile:
    def __init__(self):
        self.sort = None
        self.query = None
        self.data = None

    def create(self, data):
        self.data = data
        return database_name.mobile.insert_one(self.data)

    def read(self, query, sort):
        self.query = query
        self.sort = sort
        return database_name.mobile.find_one(self.query, self.sort)

    def update(self, query, sort):
        self.query = query
        self.sort = sort
        return database_name.mobile.update_one(self.query, self.data)
