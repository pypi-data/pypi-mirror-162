import json
import logging
import unittest

import firebase_admin
from firebase_admin import credentials

import upswingutil as ul
from upswingutil.channel import trigger_reservation_email, TriggerReservationEmailModel, SendEmailModel
from upswingutil.db import Firestore
from upswingutil.resource import access_secret_version


class TestFirestore(unittest.TestCase):
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
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

    def test_sending_invite(self):
        data = TriggerReservationEmailModel(
            orgId='11281',
            hotelId='11282',
            hotelName='Test 1',
            reservationId='206238',
            firstName='Harsh',
            lastName='Mathur',
            guestEmail='harsh@upswing.global',
            arrivalDate='2022-07-15 14:00:00',
            departureDate='2022-07-30 14:00:00'
        )
        trigger_reservation_email(data)

