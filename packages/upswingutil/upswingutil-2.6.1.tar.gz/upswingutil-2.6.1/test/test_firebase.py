import json
import logging
import unittest

import firebase_admin
from firebase_admin import credentials

import upswingutil as ul
from upswingutil.resource import access_secret_version, FirebaseHelper, setup_logging


class TestFirestore(unittest.TestCase):
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
    ul.ENCRYPTION_SECRET = "S1335HwpKYqEk9CM0I2hFX3oXa5T2oU86OXgMSW4s6U="
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

    def test_find_user_by_email(self):
        fb = FirebaseHelper('alvie')
        result = fb.find_user_by_email('harsh@upswing.global2')
        if result:
            logging.info(f'User found UID: {result.uid}')

    def test_creating_user_by_email(self):
        fb = FirebaseHelper('alvie')
        result = fb.create_user_by_email('vikash@upswing.global')
        assert result.uid is not None
        if result:
            logging.info(f'User: {result.uid}')
