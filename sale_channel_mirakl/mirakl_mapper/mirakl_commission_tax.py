from pydantic import BaseModel


class MiraklCommissionTax(BaseModel):
    amount: float
    code: str
    rate: float
