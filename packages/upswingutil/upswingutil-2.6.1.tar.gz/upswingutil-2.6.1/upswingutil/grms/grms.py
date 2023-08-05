
from loguru import logger
from upswingutil.db import Firestore, Mongodb
from upswingutil.integrations.models import Providers
from upswingutil.schema import ResponseDict, CheckinReservationModel


def grms_activation(orgId: str, data: CheckinReservationModel, auth_token: str) -> ResponseDict:
    """
        Generate grms link for given reservation with respect to which grms provider is linked with the given room
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
        if room_mapping['grmsProvider'] is not None and room_mapping['grmsProvider'] != '' and room_mapping[
            'grmsId'] != '':
            if room_mapping['grmsProvider'] == Providers.MESSERCHMITT.value:
                response = messerchmitt_grms_activation(room_mapping)
            elif room_mapping['grmsProvider'] == Providers.ASSA_ABLOY.value:
                raise Exception(f"GRMS not implemented yet for {room_mapping['grmsProvider']}")
            else:
                raise Exception(f"GRMS not implemented yet for {room_mapping['grmsProvider']}")

            if response.status:
                response = post_grms_linking(orgId, data, response.data)

        else:
            response.message = f'GRMS not mapped for room {orgId} : {data.hotelId} : {data.roomId}'
            logger.info(response.message)
    except Exception as e:
        response.message = f'Error linking GRMS to reservation {orgId} : {data.reservationId}'
        logger.error(response.message)
        logger.error(e)
    finally:
        mongo.close_connection()
        return response


def post_grms_linking(orgId: str, data: CheckinReservationModel, grms: dict) -> ResponseDict:
    """
        This function takes care of linking grms to respective reservation and notifying the guest for the same
        @author: harsh
        :param orgId: the hotel chain
        :param data: check in details
        :param grms: grms linked to the room
        :return: response dict with details
        """
    response = ResponseDict()
    mongo = Mongodb(orgId)
    fireDB = Firestore('alvie')
    fireDB.get_collection(f'Organizations/{orgId}/reservations').document(data.reservationId).set({'grms': grms},
                                                                                                  merge=True)
    result = mongo.get_collection(mongo.RESERVATION_COLLECTION).update_one({'_id': data.reservationId}, {
        '$set': {
            'grms': grms
        }
    }, upsert=True)
    if result.acknowledged:
        response.status = True
        response.message = f'GRMS linked to reservation {orgId} : {data.reservationId}'
        logger.info(response.message)
    return response


def messerchmitt_grms_activation(room_mapping: dict) -> ResponseDict:
    """
        This function gets messerchmitt grms device for the given room guest is staying in
        @author: harsh
        :param room_mapping: doorlock room to which this reservation is linked
        :return: response dict with status
    """
    response = ResponseDict()
    response.status = True
    response.data = {
        'roomId': room_mapping.get('grmsId'),
        'enabled': True
    }
    return response
