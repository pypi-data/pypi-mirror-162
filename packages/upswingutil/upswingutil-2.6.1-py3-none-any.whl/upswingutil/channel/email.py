import datetime
import logging
import smtplib
from email.message import EmailMessage
from typing import List, Optional

from googleapiclient.discovery import build
from pydantic import BaseModel

import upswingutil as ul
from upswingutil.db import Mongodb, Firestore
from upswingutil.resource import decrypt
from upswingutil.schema import ResponseDict


class ParameterModel(BaseModel):
    orgId: str
    toList: str
    smtpHost: str
    smtpPort: str
    fromEmail: str  # //use .decode('utf-8')
    password: str  # //use .decode('utf-8')
    subject: str
    template: str
    source: str
    campaignId: str
    reservationId: str


class SendEmailModel(BaseModel):
    orgId: str
    toEmail: str
    smtpHost: str
    smtpPort: str
    fromEmail: str  # //use .decode('utf-8')
    password: str  # //use .decode('utf-8')
    subject: str
    template: str
    source: str
    campaignId: Optional[str]
    reservationId: Optional[str]


class TriggerReservationEmailModel(BaseModel):
    orgId: str
    hotelId: str
    hotelName: str
    reservationId: str
    firstName: str
    lastName: str = ''
    guestEmail: str
    arrivalDate: str
    departureDate: str


def build_template(template: str, v_name: List, r_name: List):
    i = 0
    for v in v_name:
        template = template.replace(v, r_name[i])
        i = i + 1
    return template


def generate_template(template: str, key_value_pair: dict) -> str:
    return template.format(**key_value_pair)


def send_email(record: SendEmailModel):
    response = ResponseDict(status=False, message="Init Message", data={})
    logging.info(f"{record} - {datetime.datetime.utcnow()}")
    mongo = Mongodb(record.orgId)
    try:
        msg = EmailMessage()
        msg['Subject'] = f"{record.subject}"
        msg['From'] = decrypt(record.fromEmail.encode('utf-8'))
        msg['To'] = record.toEmail
        msg.set_content(f"{record.template}", subtype='html')

        with smtplib.SMTP_SSL(record.smtpHost, record.smtpPort) as smtp_client:
            smtp_client.login(decrypt(record.fromEmail.encode('utf-8')),
                              decrypt(record.password.encode('utf-8')))
            smtp_client.send_message(msg)
            smtp_client.quit()
            logging.info(f"Email Sent - {record.toEmail}")
        __post_sending_email__(mongo, record)
        response.status = True
    except Exception as e:
        logging.error(e)
        logging.error(f"Unable to send email to {record.toEmail}")
        _update_report = mongo.get_collection(mongo.OFFERS_CAMPAIGN_COLLECTION).update_one(
            {'_id': record.campaignId}, {
                '$inc': {'reports.email.pushed': 1}}, upsert=True)
        response.status = False
        response.message = e.__str__()
    finally:
        mongo.close_connection()
        return response.dict()


def __post_sending_email__(mongo, record: SendEmailModel):
    try:
        if record.source == 'campaign':
            logging.info('updating campaign report')
            _update_report = mongo.get_collection(mongo.OFFERS_CAMPAIGN_COLLECTION).update_one(
                {'_id': record.campaignId}, {
                    '$inc': {'reports.email.pushed': 1, 'reports.email.delivered': 1}}, upsert=True)

        elif record.source == 'reservation':
            logging.info('updating guest email record')
            __pipeline__ = [
                {
                    '$match': {
                        '_id': record.reservationId
                    }
                }, {
                    '$unwind': {
                        'path': '$guestInfo.guest_list'
                    }
                }, {
                    '$lookup': {
                        'from': 'guests',
                        'localField': 'guestInfo.guest_list.guest',
                        'foreignField': '_id',
                        'as': 'guest_data'
                    }
                }, {
                    '$unwind': {
                        'path': '$guest_data'
                    }
                }, {
                    '$project': {
                        'guestId': '$guestInfo.guest_list.guest',
                        'firstName': '$guest_data.firstName',
                        'lastName': '$guest_data.lastName',
                        'email': '$guest_data.contactInfo.email',
                        'mobile': '$guest_data.contactInfo.mobile'
                    }
                }
            ]
            result = mongo.execute_pipeline(mongo.RESERVATION_COLLECTION, __pipeline__)
            _guest = result[0] if len(result) > 0 else {}
            _update_report = mongo.get_collection(mongo.APP_USERS_MANAGEMENT_COLLECTION).update_one(
                {'firstName': _guest['firstName'], 'lastName': _guest['lastName'], 'email': _guest['email'],
                 'mobile': _guest['mobile'], 'bookings.reservationId': record.reservationId},
                {'$set': {'bookings.$.welcome_email.sendStatus': True,
                          'bookings.$.welcome_email.sentAt': datetime.datetime.utcnow()}}, upsert=True)
    except Exception as e:
        logging.error(e)
        logging.error(f"Unable to perform post email action for {record.toEmail}")


def create_dataflow_job_for_sending_emails(jobname: str, parameters: ParameterModel):
    dataflow = build('dataflow', 'v1b3')
    request = dataflow.projects().locations().templates().launch(
        projectId=ul.G_CLOUD_PROJECT,
        location='asia-south1',
        gcsPath="gs://dataflow-content/Communication/EmailTrigger/templates/email_trigger",
        body={
            'jobName': jobname,
            'parameters': parameters.dict()
        }
    )
    response = request.execute()
    return response


def trigger_reservation_email(data: TriggerReservationEmailModel):
    response = ResponseDict(status=False, message="Init", data={})
    mongo = Mongodb(data.orgId)
    _smtp_record = mongo.get_collection(mongo.INTEGRATION_PROPERTY).find_one(
        {"_id": f"{data.hotelId}-welcome-email", "hotelId": data.hotelId})
    org: dict = Firestore('alvie').get_ref_document(f'Organizations', data.orgId).to_dict()
    if _smtp_record is None:
        logging.error(f"Welcome Email not configured and SMTP Records are none")
    elif _smtp_record['allow_welcome_email']:
        template_data = {
            'logo': org.get('logo'),
            'hotelName': data.hotelName,
            'reservationId': data.reservationId,
            'firstName': data.firstName,
            'lastName': data.lastName,
            'webAppURL': org.get('appURL').get('webAppURL'),
            'googlePlayURL': org.get('appURL').get('googlePlayURL'),
            'appStoreURL': org.get('appURL').get('appStoreURL'),
            'arrivalDate': data.arrivalDate
        }
        _smtp_record['template'] = generate_template(_smtp_record['template'], template_data)
        parameters = SendEmailModel(
            orgId=data.orgId,
            toEmail=data.guestEmail,
            smtpHost=_smtp_record['smtp_host'],
            smtpPort=_smtp_record['smtp_port'],
            fromEmail=f"{_smtp_record['emailId'].decode('utf-8')}",  # to convert it to string
            password=f"{_smtp_record['password'].decode('utf-8')}",  # to convert it to string
            subject=f"Welcome {data.firstName} to {data.hotelName}",
            template=_smtp_record['template'],
            source='reservation',
            campaignId='',
            reservationId=data.reservationId
        )

        _se_flag = send_email(parameters)
        if _se_flag['status']:
            response.status = True
        else:
            response.message = _se_flag['message']

        # res = create_dataflow_job_for_sending_emails(
        #     jobname=f"{data.orgId}-{data.hotelId}-WelcomeEmail-{data.reservationId}-{sent_time}", parameters=parameters)
        # if 'job' in res:
        #     logging.info(f"Successfully Created the Welcome Email Job: {data.guestEmail}")
        #     mongo.close_connection()
        #     return True
        # else:
        #     mongo.close_connection()
        #     return False
    else:
        logging.info(f"Welcome Email disabled for {data.orgId} : {data.hotelId}")

    return response.dict()
