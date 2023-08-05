import unittest
# from upswingutil.ml import ReservationCountForecast
import upswingutil as ul
# from upswingutil.pms.oracle import NAME as ORACLE
# from upswingutil.pms.rms import NAME as RMS
from upswingutil.db import Mongodb

ul.ENCRYPTION_SECRET = "S1335HwpKYqEk9CM0I2hFX3oXa5T2oU86OXgMSW4s6U="
ul.MONGO_URI = "mongodb://AdminUpSWingGlobal:AdMinUpswingtr012325r@dev.db.upswing.global:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
ul.G_CLOUD_PROJECT = "aura-staging-31cae"
ul.FIREBASE = "/Users/harsh/upswing/github/api-oracle/SECRET/aura-staging-31cae-firebase-adminsdk-dyolr-7c135838e9.json"
ul.LOG_LEVEL_VALUE = 'DEBUG'


class TestMongodb(unittest.TestCase):

    def test_connecting_to_mongodb(self):
        mongo = Mongodb('OHIPSB')
        result = mongo.get_collection(mongo.RESERVATION_COLLECTION).count()
        print(f'This collection has {result} records')
        mongo.close_connection()

    def test_query_mongodb(self):
        mongo = Mongodb('11249')
        result = mongo.get_collection(mongo.RESERVATION_COLLECTION).find({'_id': 6},
                                                                         {'accountId': 1, 'activityId': 1, 'areaId': 1,
                                                                          'booking_type': 1})
        for item in result:
            print(item)
        mongo.close_connection()

    def test_aggregate_pipeline(self):
        mongo = Mongodb('11249')
        propertyId = 11264
        __pipeline__ = [
            {
                '$match': {
                    'clientId': propertyId
                }
            }, {
                '$group': {
                    '_id': '$booking_type',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        result = mongo.execute_pipeline(mongo.RESERVATION_COLLECTION, __pipeline__)
        for item in result:
            print(f'{item["_id"]} has {item["count"]} entries')
        mongo.close_connection()

    ## Before running this uncomment def return_db_collection(self):
    def test_clone_db(self):
        mongo1 = Mongodb('11281')
        mongo2 = Mongodb('tajBusinessBay')

        for coll in mongo1.return_db_collection():
            print(f"{coll} copying")

            result = mongo1.get_collection(f'{coll}').find()
            mongo2.get_collection(f'{coll}').insert_many(result)

            for data in result:
                mongo2.get_collection(mongo2.RESERVATION_COLLECTION).insert_one(data)
            print(f"{coll} copying completed")


if __name__ == '__main__':
    print('testing resv sync')
    TestMongodb()
    print('completed')
