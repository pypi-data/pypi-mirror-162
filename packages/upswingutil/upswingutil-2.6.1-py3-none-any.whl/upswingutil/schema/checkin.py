from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class GuestType(str, Enum):
    PRIMARY = 'Primary'
    CO_TRAVELLER = 'Co-traveller'
    SPOUSE = 'Spouse'
    CHILDREN = 'Children'


class CheckInGuestModel(BaseModel):
    name: str = ""
    guestEmail: str = ""
    guestPMSId: str = ""
    appGuestUID: str = ""
    guestType: GuestType = GuestType.CO_TRAVELLER
    primary: bool = ""
    appAccess: bool = ""
    doorlockAccess: bool = ""
    grmsAccess: bool = ""
    doorlockKey: Optional[str] = ""
    doorlockSpecialAccess: Optional[str] = ""


class CheckinReservationModel(BaseModel):
    reservationId: str
    hotelId: str
    arrivalDate: str = ""
    departureDate: str = ""
    roomId: str = ""
    checkin_type: str = ""
    doorlockLinked: bool = False
    grmsLinked: bool = False
    appLinked: bool = False
    guest_list: List[CheckInGuestModel] = []

