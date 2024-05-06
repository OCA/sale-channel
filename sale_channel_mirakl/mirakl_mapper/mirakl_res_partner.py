from typing import Optional

from pydantic import BaseModel

from odoo import Command

from .mirakl_billing_address import MiraklBillingAddress
from .mirakl_shipping_address import MiraklShippingAddress


class MiraklResPartner(BaseModel):
    billing_address: MiraklBillingAddress
    civility: str = ""
    customer_id: str  # required
    firstname: str | None  # required, Can be None
    lastname: str = ""
    locale: str = ""
    shipping_address: MiraklShippingAddress
    shipping_zone_code: Optional[str] = None  # not required, Can be None
    company: str = None
    country_iso_code: Optional[str] = None

    @classmethod
    def build_mirakl_customer(cls, data: dict):
        return cls(**data)

    def build_name(self):
        name = (
            " ".join([self.lastname, self.firstname])
            if self.firstname
            else self.lastname
        )
        name = "{}, {}".format(self.company, name) if self.company else name
        return name

    def build_country_id(self, sale_channel):

        if self.country_iso_code:
            country = sale_channel.env["res.country"].search(
                [("code", "=", self.country_iso_code)],
                limit=1,
            )
        elif self.shipping_zone_code:
            country = sale_channel.env["res.country"].search(
                [("code", "=", self.shipping_zone_code)],
                limit=1,
            )
        else:
            country = sale_channel.default_country_id
        return country

    def odoo_model_dump(self, mirakl_channel):
        country = self.build_country_id(mirakl_channel)
        return {
            "name": self.build_name(),
            "country_id": country.id,
            "channel_ids": [Command.link(mirakl_channel.channel_id.id)],
            "is_from_mirakl": True,
        }
