import json
import logging
import unittest

import firebase_admin
from firebase_admin import credentials

import upswingutil as ul
from upswingutil.db import Firestore
from upswingutil.pms import checkin, post_check_in_reservation
from upswingutil.resource import access_secret_version, setup_logging
from upswingutil.schema import CheckinReservationModel


class TestCheckIn(unittest.TestCase):
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
    ul.ENCRYPTION_SECRET = "S1335HwpKYqEk9CM0I2hFX3oXa5T2oU86OXgMSW4s6U="
    ul.MONGO_URI = access_secret_version(ul.G_CLOUD_PROJECT, 'MONGOURI', '5')
    ul.LOG_LEVEL_VALUE = logging.DEBUG

    cred = json.loads(
        access_secret_version(ul.G_CLOUD_PROJECT, 'Firebase-Aura', '1'))
    cred = credentials.Certificate(cred)
    firebase_admin.initialize_app(cred)

    cred = json.loads(
        access_secret_version(ul.G_CLOUD_PROJECT, 'Firebase-Alvie', '3'))
    cred = credentials.Certificate(cred)
    firebase_admin.initialize_app(cred, name='alvie')

    setup_logging()

    def test_welcome_email_trigger(self):
        pass
