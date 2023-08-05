from loguru import logger

from upswingutil.db import Firestore
from upswingutil.schema import AlvieQRGenerateorModels, ResponseDict


def alvie_qr_generator(qr_data: AlvieQRGenerateorModels):
    response = ResponseDict(status=False, message="Init Message", data={})
    try:
        ref = Firestore('alvie').write_doc_auto_id(
            f"Organizations/{qr_data.orgId}/properties/{qr_data.hotelId}/integrations/qrCodes/codes", qr_data.data)
        ref_doc = ref[1].get()
        if ref_doc.exists:
            response.data = {'id': ref_doc.id}
            response.status = True
            response.message = "Successfully generated the QR Code"
    except Exception as e:
        logger.error(f"Error in generating the QR for {qr_data.orgId} - {qr_data.hotelId} - {qr_data.data}")
        logger.error(e)
        response.message = f"Error occurred - {e.__str__()}"
    finally:
        return response.dict()
