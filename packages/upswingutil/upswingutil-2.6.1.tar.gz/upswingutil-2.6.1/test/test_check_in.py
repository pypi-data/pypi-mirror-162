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

    def test_check_in_rms(self):
        orgId = '11281'
        data = CheckinReservationModel(
            reservationId='169410',
            hotelId='11282',
            arrivalDate="2022-02-02 14:00:00",
            departureDate="2022-02-05 11:00:00",
            roomId="14",
            checkin_type="manual",
            doorlockLinked=True,
            grmsLinked=True,
            appLinked=True,
            guest_list=[
                {
                    "name": "Harsh Mathur",
                    "guestEmail": "harsh@upswing.global",
                    "primary": True,
                    "guestPMSId": "1234",
                    "appGuestUID": "nfploQfXyHdi14qvv8W1ZH62wkB2",
                    "appAccess": True,
                    "doorlockAccess": True,
                    "grmsAccess": True,
                    "guestType": "Primary"
                },
                {
                    "name": "Vikash Anand",
                    "guestEmail": "vikash@upswing.global",
                    "primary": True,
                    "guestPMSId": "1235",
                    "appGuestUID": "",
                    "appAccess": True,
                    "doorlockAccess": True,
                    "grmsAccess": False,
                    "guestType": "Co-traveller"
                }
            ]
        )
        response = checkin(orgId, data)
        assert response.status
        assert response.message == 'Complete check-in done successfully'
        assert response.data['check_in_guest_count'] == len(data.guest_list)

    def test_check_in_opera(self):
        orgId = 'tajBusinessBay'
        data = CheckinReservationModel(
            hotelId='11282',
            reservationId='169410',
            arrivalDate="2022-02-02 14:00:00",
            departureDate="2022-02-05 11:00:00",
            roomId="14",
            checkin_type="manual",
            doorlockLinked=True,
            grmsLinked=True,
            appLinked=True,
            guest_list=[
                {
                    "name": "Harsh Mathur",
                    "guestEmail": "harsh@upswing.global",
                    "primary": True,
                    "guestPMSId": "1234",
                    "appGuestUID": "nfploQfXyHdi14qvv8W1ZH62wkB2",
                    "appAccess": True,
                    "doorlockAccess": True,
                    "grmsAccess": True,
                    "guestType": "Primary"
                },
                {
                    "name": "Vikash Anand",
                    "guestEmail": "vikash@upswing.global",
                    "primary": True,
                    "guestPMSId": "1235",
                    "appGuestUID": "",
                    "appAccess": True,
                    "doorlockAccess": True,
                    "grmsAccess": False,
                    "guestType": "Co-traveller"
                }
            ]
        )
        response = checkin(orgId, data)
        assert response.status
        assert response.message == 'Complete check-in done successfully'
        assert response.data['check_in_guest_count'] == len(data.guest_list)

    def test_post_check_in_rms(self):
        orgId = '11281'
        db = Firestore('alvie')
        data = CheckinReservationModel(
            reservationId='169410',
            hotelId='11282',
            arrivalDate="2022-02-02 14:00:00",
            departureDate="2022-02-05 11:00:00",
            roomId="14",
            checkin_type="manual",
            doorlockLinked=True,
            grmsLinked=True,
            appLinked=True,
            guest_list=[
                {
                    "name": "Alex",
                    "guestEmail": "alex@gmail.com",
                    "primary": True,
                    "guestPMSId": "1234",
                    "appGuestUID": "CvbKhCxAgQeZ030isXyOHplZaj93",
                    "appAccess": True,
                    "doorlockAccess": True,
                    "grmsAccess": True,
                    "guestType": "Primary"
                },
                {
                    "name": "Harsh Mathur",
                    "guestEmail": "harsh@upswing.global",
                    "primary": False,
                    "guestPMSId": "1235",
                    "appGuestUID": "",
                    "appAccess": True,
                    "doorlockAccess": True,
                    "grmsAccess": False,
                    "guestType": "Co-traveller"
                }
            ]
        )
        response = post_check_in_reservation(db, orgId, data)
        assert response.status
