import logging
from upswingutil.db import Firestore
from upswingutil.db.model import ReservationModelV2
from upswingutil.schema import GuestType


def store_reservation_to_alvie(record: ReservationModelV2):
    try:
        alvieDB = Firestore(app='alvie')
        record = record.to_mongo()
        for guest in record.get('guestInfo').get('guest_list'):
            guest = dict(guest)
            # to store reservation only in the profile of the primary guest
            # incase if we have to make it store for all the guests, then remove this condition
            if guest.get('primary'):
                docs = alvieDB.get_collection(f'Organizations/{record.get("orgId")}/users') \
                    .where("pmsGuestProfile", "==", guest.get('guest')).stream()
                for doc in docs:
                    alvieDB.get_collection(f'Organizations/{record.get("orgId")}/users/{doc.id}/reservations') \
                        .document(str(record.get('_id'))).set(record, merge=True)
                    logging.info(
                        f"reservation {record.get('orgId')} : {record.get('_id')} added to alvie profile {doc.id}")
    except Exception as e:
        logging.error(f'Error while storing reservation {record.get("orgId")} : {record.get("_id")} to firestore')
        logging.error(e)


def store_reservation_to_alvie_v2(record: ReservationModelV2):
    """
    Store the reservation into firestore only if the user's profile available in firestore to link with
    Args:
        record: reservation record version 2
    Author: Harsh Mathur
    """
    try:
        alvieDB = Firestore(app='alvie')
        record = record.to_mongo()
        for guest in record.get('guestInfo').get('guest_list'):
            guest = dict(guest)
            guestUID = guest.get('appGuestUID')
            if guestUID and guestUID is not '':
                record['guest_app_data'][guestUID] = {
                    'appAccess': True,
                    'primary': guest.get('primary'),
                    'doorlockAccess': True,
                    'grmsAccess': True,
                    'overallRating': 0,
                    'overallReview': '',
                    'guestType': GuestType.PRIMARY if guest.get('primary') else GuestType.CO_TRAVELLER
                }
        alvieDB.get_collection(f'Organizations/{record.get("orgId")}/reservations') \
            .document(str(record.get('_id'))).set(record, merge=True)
        logging.info(f"reservation {record.get('orgId')} : {record.get('_id')} added to firestore")
    except Exception as e:
        logging.error(f'Error while storing reservation {record.orgId} : {record.id} to firestore')
        logging.error(e)
