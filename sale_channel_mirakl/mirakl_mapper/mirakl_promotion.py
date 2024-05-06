from typing import List

from .mirakl_json import MiraklJson


class MiraklPromotion(MiraklJson):
    applied_promotions: List[str]
    total_deduced_amount: float
