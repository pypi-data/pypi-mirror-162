import logging

from upswingutil.db import Firestore
from upswingutil.schema import ResponseDict, CheckinReservationModel


def check_in_reservation(db: Firestore, orgId: str, data: CheckinReservationModel) -> ResponseDict:
    response = ResponseDict()
    pass
