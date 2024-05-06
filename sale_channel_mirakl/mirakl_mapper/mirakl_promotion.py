from typing import List

from pydantic import BaseModel


class MiraklPromotion(BaseModel):
    applied_promotions: List[str]
    total_deduced_amount: float
