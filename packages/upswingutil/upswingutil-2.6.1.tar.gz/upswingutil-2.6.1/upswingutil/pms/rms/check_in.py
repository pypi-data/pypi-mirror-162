import logging
import requests
from upswingutil.db import Firestore
from upswingutil.pms.rms import get_key
from upswingutil.schema import ResponseDict, Token, CheckinReservationModel


def check_in_reservation(orgId: str, data: CheckinReservationModel) -> ResponseDict:
    result = ResponseDict()
    token: Token = get_key(orgId)
    header = {
        'Content-Type': 'application/json',
        'authtoken': token.key
    }
    _url = f"{token.hostName}/reservations/{data.reservationId}/status"
    response = requests.put(_url, headers=header, data="{'status': 'arrived'}")
    if response.status_code != 200:
        logging.error(f'failed to update status in RMS {response.status_code} : {response.reason} : {response.content}')
        result.message = f'failed to update status in RMS {response.status_code} : {response.reason} : {response.content}'
    else:
        result.status = True
        result.data = response.json()
    return result
