from pydantic import BaseModel


class AlvieQRGenerateorModels(BaseModel):
    orgId: str
    hotelId: str
    data: dict
