import datetime
import logging

from upswingutil.db import Firestore, Mongodb
from upswingutil.schema import ResponseDict, CheckinReservationModel
from upswingutil.db.model import ReservationModelV2, Status


def check_in_reservation(db: Firestore, agent, orgId: str, data: CheckinReservationModel) -> ResponseDict:
    response = ResponseDict()
    mongo = Mongodb(orgId)
    reservation = ReservationModelV2(
        _id=data.reservationId,
        orgId=orgId,
        agent=agent,
        datesAndDuration={
            'createdDate': datetime.datetime.now(),
            'confirmedDate': datetime.datetime.now(),
            'arrivalDate': data.arrivalDate,
            'departureDate': data.arrivalDate,
            'cancelledDate': '',
        },
        status=Status.ARRIVED.value,
        property={
            'hotelId': data.hotelId,
            'roomId': data.roomId,
            'roomName': data.roomId,
            'categoryName': '',
            'numberOfRooms': 1,
        },
        auraRecordUpdatedOn=datetime.datetime.now()
    )
    result = mongo.get_collection(mongo.RESERVATION_COLLECTION)\
        .update_one(
            {'_id': data.reservationId},
            {'$set': reservation.to_mongo()},
            upsert=True
        )
    if result.acknowledged:
        db.get_collection(f'Organizations/{orgId}/reservations').document(data.reservationId).set(reservation.to_mongo(), merge=True)
        response.status = True
    return response
