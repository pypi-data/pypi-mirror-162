from loguru import logger
from upswingutil.db import Firestore, Mongodb
from upswingutil.resource import http_retry, FirebaseHelper
from upswingutil.schema import ResponseDict, CheckinReservationModel
from upswingutil.integrations.models import Providers


def doorlock_activation(orgId, data: CheckinReservationModel, auth_token: str) -> ResponseDict:
    """
    Generate doorlock for given reservation with respect to which doorlock provider is linked with the given room
    @author: harsh
    :param orgId:
    :param data: check-in details
    :param auth_token: for accessing upswing's messerchmitt server
    :return: response dict
    """
    response = ResponseDict()
    mongo = Mongodb(orgId)
    try:
        room_mapping = mongo.get_collection(mongo.IOT_ROOM_MAPPING).find_one(
            {'hotelId': data.hotelId, 'pmsRoomId': data.roomId})
        if room_mapping['doorlockProvider'] is not None and room_mapping['doorlockProvider'] != '' and room_mapping['doorlockId'] != '':
            if room_mapping['doorlockProvider'] == Providers.MESSERCHMITT.value:
                response = messerchmitt_doorlock_activation(orgId, data, room_mapping, auth_token)
            elif room_mapping['doorlockProvider'] == Providers.ASSA_ABLOY.value:
                raise Exception(f'Doorlock not implemented yet for {room_mapping["doorlockProvider"]}')
            else:
                raise Exception(f'Doorlock not implemented yet for {room_mapping["doorlockProvider"]}')

            if response.status:
                response = post_doorlock_creation(orgId, data, response.data)
        else:
            response.message = f'Doorlock not mapped for room {orgId} : {data.hotelId} : {data.roomId}'
            logger.info(response.message)
        response.status = True
    except Exception as e:
        response.message = f'Failed to generate doorlock for {orgId} : {data.reservationId}'
        logger.error(response.message)
        logger.error(e)
    finally:
        mongo.close_connection()
        return response


def post_doorlock_creation(orgId, data: CheckinReservationModel, doorLocks: dict) -> ResponseDict:
    """
    This function takes care of storing the generated doorlock to respective profiles and notifying the guest for the same
    @author: harsh
    :param orgId: the hotel chain
    :param data: check in details
    :param doorLocks: doorlock of each guest profile
    :return: response dict with details
    """
    response = ResponseDict()
    mongo = Mongodb(orgId)
    fireDB = Firestore('alvie')
    for uid in doorLocks.keys():
        data_to_update = {
            f'guest_app_data.{uid}.doorlockKey': doorLocks.get(uid).get('doorlockKey'),
            f'guest_app_data.{uid}.doorlockSpecialAccess': doorLocks.get(uid).get('doorlockSpecialAccess')
        }
        fireDB.get_collection(f'Organizations/{orgId}/reservations').document(data.reservationId).set({
            'guest_app_data': {
                uid: {
                    'doorlockKey': doorLocks.get(uid).get('doorlockKey'),
                    'doorlockSpecialAccess': doorLocks.get(uid).get('doorlockSpecialAccess')
                }
            }
        }, merge=True)
        mongo.get_collection(mongo.RESERVATION_COLLECTION).find_one_and_update(
            {'_id': data.reservationId},
            {
                '$set': data_to_update
            },
            upsert=True
        )
    mongo.close_connection()
    response.status = True
    response.message = f'Doorlock generated for {len(doorLocks.keys())} profiles in {orgId} : {data.reservationId}'
    logger.info(response.message)
    return response


def messerchmitt_doorlock_activation(orgId, data: CheckinReservationModel, room_mapping, auth_token) -> ResponseDict:
    """
    This function generated messerchmitt doorlock key for each guest in reservation
    @author: harsh
    :param orgId:
    :param data: check-in reservation details
    :param room_mapping: doorlock room to which this reservation is linked
    :param auth_token: to access upswing's messerchmitt server
    :return: response dict with status
    """
    response = ResponseDict()
    mongo = Mongodb(orgId)
    upswingDB = Mongodb('Upswing')
    fb = FirebaseHelper('alvie')
    header = {'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    http = http_retry()

    mstUpswingServer = upswingDB.get_collection("integrations").find_one(
        {
            'integration_type': 'doorlock',
            'provider': Providers.MESSERCHMITT.value,
            'solution_type': 'cloud'
        }
    )
    upswingDB.close_connection()
    _url = f"{mstUpswingServer['baseURL']}/v0/mst/doorlock/get/key"
    property_doorlock_config = mongo.get_collection(mongo.INTEGRATION_PROPERTY).find_one(
        {"provider": Providers.MESSERCHMITT.value, "hotelId": data.hotelId, "integration_type": "doorlock"},
        {"sa_guest": 1}
    )
    mongo.close_connection()
    special_area_request = ''
    if property_doorlock_config:
        special_area_request = property_doorlock_config['sa_guest']

    for guest in data.guest_list:
        guestUID = fb.find_user_by_email(guest.guestEmail)
        if guestUID:
            guestUID = guestUID.uid
            payload = {
                "orgId": orgId,
                "hotelId": data.hotelId,
                "doorlockRoomId": room_mapping['doorlockId'],
                "uid": guestUID,
                "sa_guest": special_area_request,
                "checkout_date": data.departureDate
            }
            try:
                result = http.post(url=_url, json=payload, headers=header, timeout=30)
                if result.status_code != 200:
                    response.message = f'Messerchmitt doorlock request failed {result.status_code}'
                    logger.error(response.message)
                    logger.error(f'URL: {result.url}')
                    logger.error(f'URL: {result.json()}')
                else:
                    result = result.json()
                    if result.get('status'):
                        response.data[guestUID] = {
                            'doorlockKey': result.get('data')['result'],
                            'doorlockSpecialAccess': special_area_request
                        }
                    else:
                        response.message = result.get('message')
                        logger.error(response.message)
            except Exception as e:
                logger.error(e)
    response.status = True
    response.message = 'Doorlock generated by Messerchmitt'
    return response
