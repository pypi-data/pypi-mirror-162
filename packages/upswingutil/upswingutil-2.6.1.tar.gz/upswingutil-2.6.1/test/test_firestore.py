import json
import logging
import unittest

import firebase_admin
from firebase_admin import credentials

import upswingutil as ul
from upswingutil.db import Firestore
from upswingutil.resource import access_secret_version


class TestFirestore(unittest.TestCase):
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
    ul.ENCRYPTION_SECRET = "S1335HwpKYqEk9CM0I2hFX3oXa5T2oU86OXgMSW4s6U="
    ul.LOG_LEVEL_VALUE = logging.DEBUG

    cred = json.loads(
        access_secret_version(ul.G_CLOUD_PROJECT, 'Firebase-Alvie', '3'))
    cred = credentials.Certificate(cred)
    firebase_admin.initialize_app(cred)

    def test_duplicating_document(self):
        from_path = 'Organizations/11281/properties'
        to_path = 'Organizations/towerPlaza/properties'
        docName = '11282'
        db = Firestore()
        db.duplicate_document(from_path, to_path, docName)

    def test_duplicating_collection(self):
        from_path = 'Organizations/11281/properties/11282/food-and-beverages'
        to_path = 'Organizations/towerPlaza/properties/11282/food-and-beverages'
        db = Firestore()
        db.duplicate_collection(from_path, to_path)
