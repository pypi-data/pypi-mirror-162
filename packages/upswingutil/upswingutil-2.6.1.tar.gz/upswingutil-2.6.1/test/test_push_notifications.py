import json
import logging
import unittest

import firebase_admin
from firebase_admin import credentials

import upswingutil as ul
from upswingutil.channel.notification import push_notification_to_aura, NotificationAuraModel, NotificationAlvieModel, \
    push_notification_to_alvie

from upswingutil.resource import access_secret_version


class TestNotifications(unittest.TestCase):
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

    def test_notification_aura(self):
        data = NotificationAuraModel(
            orgId="tajBusinessBay",
            role=["admin", "manager"],
            title="Hello there, this is a demo test",
            body="In publishing and graphic design....",
            banner="",
            actions="",
            priority="normal",
            type="RESERVATION",
            tag="Alert",
            id="12123"
        )
        d = push_notification_to_aura(data, ul.G_CLOUD_PROJECT)


    def test_notification_alvie(self):
        ul.G_CLOUD_PROJECT = 'alvie-development'
        data = NotificationAlvieModel(
            orgId="tajBusinessBay",
            title="Hello there, this is a demo test",
            body="In publishing and graphic design....",
            banner="",
            actions=["View", "Cancel"],
            priority="normal",
            type="RESERVATION",
            tag="Alert",
            id="12123",
            tokens=['']
        )
        d = push_notification_to_alvie(data, ul.G_CLOUD_PROJECT, uids=['whglMebK3nM79sKtgRu4Gx8HWUm2'])
        print("Successful Test done")