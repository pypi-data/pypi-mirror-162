import json
import logging
import unittest

import firebase_admin
from firebase_admin import credentials

import upswingutil as ul
from upswingutil.db import Firestore
from upswingutil.grms import grms_activation
from upswingutil.resource import access_secret_version, setup_logging
from upswingutil.schema import CheckinReservationModel


class TestGRMS(unittest.TestCase):
    ul.G_CLOUD_PROJECT = 'aura-staging-31cae'
    ul.G_CLOUD_PROJECT_SECONDARY = 'alvie-development'
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

    def test_grms_activation(self):
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
        token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjUwYTdhYTlkNzg5MmI1MmE4YzgxMzkwMzIzYzVjMjJlMTkwMzI1ZDgiLCJ0eXAiOiJKV1QifQ.eyJvIjoiMTEyODEiLCJyIjoiQURNSU4iLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vYXVyYS1zdGFnaW5nLTMxY2FlIiwiYXVkIjoiYXVyYS1zdGFnaW5nLTMxY2FlIiwiYXV0aF90aW1lIjoxNjU3NTA4OTgwLCJ1c2VyX2lkIjoiWHV2SThEaFNjNGJlZ0pSclRBRjlFVWNYR2dNMiIsInN1YiI6Ilh1dkk4RGhTYzRiZWdKUnJUQUY5RVVjWEdnTTIiLCJpYXQiOjE2NTc1MTcxMTEsImV4cCI6MTY1NzUyMDcxMSwiZW1haWwiOiJkZW1vQHVwc3dpbmcuY2xvdWQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiZGVtb0B1cHN3aW5nLmNsb3VkIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.InMv4giaL8O8JHKqn0q223SeEKmNPGoc0kdNLjSvIVAsI5M2ATGxt4U9zmsxnJ_zOgJ1EkcT0S9BIPsiL4_49dnKR16bRXXl4SRu7LZnQb2E1BVFSVg5hUqUiEQaFfkX70Ac-IJpoGTjICkweLHF40jl_ZNVvdPdSB8akmqZ5cne661kv3BHa9-00lVR_9YVs2JbCQEI3zZwTSRhmE7SSQZNufUN9SfkxOhYq0QyP417_notazXBx6_IrDjV6lcNkZoeUrBd9XhJSsFWzQ3q5f1O4R0JPHMGZzO097Jp9GBFgZhEtO_gZGwdax664HcHA00xu3TogKECYU3CmcMxtw'
        response = grms_activation(orgId, data, token)
        assert response.status
