import json
import logging
import unittest

import firebase_admin
from firebase_admin import credentials
from loguru import logger

import upswingutil as ul

from upswingutil.resource import access_secret_version
from upswingutil.resource.qr_codes import alvie_qr_generator
from upswingutil.schema import AlvieQRGenerateorModels


class TestQR_Generation(unittest.TestCase):
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
    # ul.G_CLOUD_PROJECT = 'alvie-development'
    ul.ENCRYPTION_SECRET = access_secret_version(ul.G_CLOUD_PROJECT, 'ENCRYPT_SECRET_KEY', 1)
    ul.MONGO_URI = access_secret_version(ul.G_CLOUD_PROJECT, 'MONGOURI', '5')
    ul.LOG_LEVEL_VALUE = logging.DEBUG

    print('Initializing default firebase app')
    cred = json.loads(
        access_secret_version(ul.G_CLOUD_PROJECT, 'Firebase-Aura', '1'))
    cred = credentials.Certificate(cred)
    firebase_admin.initialize_app(cred)

    print('Initializing alvie firebase app')
    cred = json.loads(
        access_secret_version(ul.G_CLOUD_PROJECT, 'Firebase-Alvie', '3'))
    cred = credentials.Certificate(cred)
    firebase_admin.initialize_app(cred, name='alvie')

    def test_alvie_qr(self):
        data = AlvieQRGenerateorModels(
            orgId="11281",
            hotelId="11282",
            data={"data": "test"}
        )
        d = alvie_qr_generator(data)
        logger.info(d)