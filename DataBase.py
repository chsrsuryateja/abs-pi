import pymongo
import time

class DataBase:

    def __init__(self, dbname, username, password):
        self.dbname = dbname
        self.username = username
        self.password = password
        self._initializeDB()
        self._initializeCollections()

    def _initializeDB(self):
        try:
            connection = pymongo.MongoClient('127.0.0.1',27017)
        except pymongo.errors.ConnectionFailure as e:
            time.sleep(10)
            connection = pymongo.MongoClient('127.0.0.1',27017)
        self.db = connection[self.dbname]
        self.db.authenticate(self.username, self.password)

    def _initializeCollections(self):
        self.defaultSchedule = self.db.defaultSchedule
        self.config = self.db.config
        self.currentSchedule = self.db.currentSchedule
        self.logDetails = self.db.logDetails
        self.holidayData = self.db.holidayData
        self.longBells = self.db.longBells
