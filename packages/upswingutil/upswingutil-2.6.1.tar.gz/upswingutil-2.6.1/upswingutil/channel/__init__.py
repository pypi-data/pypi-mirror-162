from enum import Enum
from .email import create_dataflow_job_for_sending_emails, trigger_reservation_email, build_template, \
    TriggerReservationEmailModel, send_email, SendEmailModel

from .notification import NotificationAlvieModel, NotificationAuraModel, push_notification_to_alvie, push_notification_to_aura, NotificationTypes


class CHANNEL(str, Enum):
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'
