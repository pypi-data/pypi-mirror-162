import upswingutil as ul
from upswingutil.pms.oracle import ReservationSync
import firebase_admin
from loguru import logger
import os

ul.ENCRYPTION_SECRET = "S1335HwpKYqEk9CM0I2hFX3oXa5T2oU86OXgMSW4s6U="
ul.MONGO_URI = "mongodb://AdminUpSwingGlobal:Upswing098812Admin0165r@dev.db.upswing.global:27017/?authSource=admin&readPreference=primary&appname=Agent%20Oracle%20Dev&ssl=false"
ul.G_CLOUD_PROJECT = "aura-staging-31cae"
ul.FIREBASE = "SECRET/aura-staging-31cae-firebase-adminsdk-dyolr-7c135838e9.json"
ul.LOG_LEVEL_VALUE = 'DEBUG'


try:
    firebase_admin.get_app()
except Exception as e:
    logger.info(e)
    logger.info('Initializing default firebase app')
    cred = firebase_admin.credentials.Certificate(
        os.getenv("FIREBASE", "/Users/harsh/upswing/github/api-oracle/SECRET/aura-staging-31cae-firebase-adminsdk-dyolr-7c135838e9.json"))
    firebase = firebase_admin.initialize_app(cred)


if __name__ == '__main__':
    print('testing resv sync')
    orgId = 'OHIPSB'
    resvId = '20908'
    hotelId = 'SAND01'
    resv = ReservationSync(orgId)
    resv.process(resvId, hotelId)
    print('completed')
