from .mirakl_json import MiraklJson


class MiraklCommissionTax(MiraklJson):
    amount: float
    code: str
    rate: float
