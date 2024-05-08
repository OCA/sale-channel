from typing import List

from .mirakl_import_mapper import MiraklImportMapper


class MiraklPromotion(MiraklImportMapper):
    applied_promotions: List[str]
    total_deduced_amount: float
