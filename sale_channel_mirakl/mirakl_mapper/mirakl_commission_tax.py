from .mirakl_import_mapper import MiraklImportMapper


class MiraklCommissionTax(MiraklImportMapper):
    amount: float
    code: str
    rate: float
