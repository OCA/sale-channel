from typing import Optional

from pydantic import BaseModel


class CountryBuilder(BaseModel):
    shipping_zone_code: Optional[str] = None  # not required, Can be None

    def build_country(self, sale_channel):
        country = super().build_country(sale_channel)
        if self.shipping_zone_code:
            country = (
                sale_channel.env["res.country"].search(
                    [("code", "=", self.shipping_zone_code)],
                    limit=1,
                )
                or country
            )
        return country
