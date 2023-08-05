
import logging
from enum import Enum
from typing import List

from pydantic import BaseModel
import upswingutil as ul
from upswingutil.db import Mongodb
from upswingutil.resource import http_retry
from upswingutil.schema import ResponseDict


class NotificationTypes(str, Enum):
    CHECK_IN = 'CHECK-IN'
    DOORLOCK = 'DOORLOCK'
    GRMS = 'GRMS'


class NotificationAuraModel(BaseModel):
    orgId: str  # id of the org
    role: List[str]  # list of roles to whom the notification will be sent
    title: str
    body: str
    banner: str
    actions: str
    priority: str
    type: NotificationTypes
    tag: str
    id: str


class NotificationAlvieModel(BaseModel):
    orgId: str
    title: str
    body: str
    banner: str
    actions: List[str]
    priority: str
    type: NotificationTypes
    tag: str
    id: str
    tokens: List[str]


def push_notification_to_aura(data: NotificationAuraModel, G_CLOUD_PROJECT: str = ul.G_CLOUD_PROJECT):
    response = ResponseDict(status=False, message="Init", data={})
    try:
        url = f'https://asia-south1-{G_CLOUD_PROJECT}.cloudfunctions.net/notification'
        http_client = http_retry()
        _response_ = http_client.post(url, json=data.dict(), headers={'content-type': 'application/json'})
        if _response_.status_code != 200:
            response.message = "Unable to send notification" + _response_.reason
        else:
            response.status = True
            response.message = "Sent successfully"
    except Exception as e:
        logging.error(f"Unable to send notification to Aura: {data.orgId} - {data.title}")
        response.message = e.__str__()
    finally:
        return response.dict()


def push_notification_to_alvie(data: NotificationAlvieModel, G_CLOUD_PROJECT: str = ul.G_CLOUD_PROJECT,
                               guestIds: List[str] = [], uids: List[str] = []):
    response = ResponseDict(status=False, message="Init", data={})
    try:
        mongo = Mongodb(data.orgId)
        __pipeline__ = [
            {
                '$match': {
                    '$or': [
                        {
                            'pms_guestId': {
                                '$in': guestIds
                            }
                        }, {
                            'guestId': {
                                '$in': uids
                            }
                        }
                    ]
                }
            }, {
                '$project': {
                    '_id': 0,
                    'token': 1
                }
            }
        ]
        _tokens = mongo.execute_pipeline(mongo.ALVIE_SUBSCRIPTIONS_COLLECTION, __pipeline__)
        if len(_tokens) > 0:
            data.tokens = []
            [data.tokens.append(x['token']) for x in _tokens]
            url = f'https://asia-south1-{G_CLOUD_PROJECT}.cloudfunctions.net/notification'
            http_client = http_retry()
            _response_ = http_client.post(url, json=data.dict(), headers={'content-type': 'application/json'})
            if _response_.status_code != 200:
                response.message = "Unable to send notification" + _response_.reason
            else:
                response.status = True
                response.message = "Sent successfully"
        else:
            response.status = True
            response.message = "No Subscriptions found"
    except Exception as e:
        logging.error(f"Unable to send notification to Aura: {data.orgId} - {data.title}")
        response.message = e.__str__()
    finally:
        return response.dict()
