import logging
from enum import Enum
from .alvie import store_reservation_to_alvie, store_reservation_to_alvie_v2
from .rms import check_in_reservation as rms_check_in_reservation
from .oracle import check_in_reservation as oracle_check_in_reservation
from .oracle_opera import check_in_reservation as opera_check_in_reservation
from ..db import Firestore, Mongodb
from ..db.model import Status
from ..resource import FirebaseHelper
from ..schema import ResponseDict, CheckinReservationModel


class PMS(str, Enum):
    ORACLE = 'ORACLE'
    RMS = 'RMS'
    OPERA = 'ORACLE-OPERA'


def checkin(orgId: str, data: CheckinReservationModel) -> ResponseDict:
    response = ResponseDict()
    try:
        db = Firestore('alvie')
        pms = db.get_ref_document('Organizations', orgId).to_dict()
        pms = pms['pms']['name']

        if pms == PMS.RMS:
            response = rms_check_in_reservation(orgId, data)
        elif pms == PMS.ORACLE:
            response = oracle_check_in_reservation(db, orgId, data)
        elif pms == PMS.OPERA:
            response = opera_check_in_reservation(db, pms, orgId, data)

        # post successful check-in
        if response.status:
            response = post_check_in_reservation(db, orgId, data)
    except Exception as e:
        logging.error(f'Error check-in pms for {orgId}')
        logging.error(e)
        response.status = False
        response.message = f'Error check-in pms for {orgId}'
    finally:
        return response


def post_check_in_reservation(db: Firestore, orgId: str, data: CheckinReservationModel) -> ResponseDict:
    response = ResponseDict()
    try:
        fb = FirebaseHelper('alvie')
        guest_app_data = {}
        mongo = Mongodb(orgId)
        for guest in data.guest_list:
            uid = guest.appGuestUID
            if uid == '' or uid is None:
                _user = fb.create_user_by_email(guest.guestEmail, guest.name)
                if _user:
                    uid = _user.uid

            guest_app_data[uid] = {
                'name': guest.name,
                'guestEmail': guest.guestEmail,
                'appAccess': guest.appAccess,
                'primary': guest.primary,
                'doorlockAccess': guest.doorlockAccess,
                'grmsAccess': guest.grmsAccess,
                'guestType': guest.guestType,
            }
            logging.debug(f'User {uid} is ready to be saved to reservation {orgId} : {data.reservationId}')
        data_to_update = {
            'status': Status.ARRIVED.value,
            'guest_app_data': guest_app_data
        }
        mongo.get_collection(mongo.RESERVATION_COLLECTION).update_one(
            {'_id': data.reservationId},
            {
                '$set': data_to_update
            },
            upsert=True
        )

        db.get_collection(f'Organizations/{orgId}/reservations').document(data.reservationId).set(data_to_update, merge=True)
        response.status = True
        response.message = f'Complete check-in done successfully for {orgId} : {data.reservationId}'
        response.data = {
            'check_in_guest_count': len(data.guest_list)
        }
        logging.info(response.message)
    except Exception as e:
        response.message = 'Failed in post pms check-in procedure'
        raise e
    finally:
        return response
