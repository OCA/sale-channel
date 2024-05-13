from typing import Optional

from pydantic import BaseModel

from odoo import Command


class ResPartnerBuilder(BaseModel):
    civility: str = ""
    company: str = None
    firstname: str | None  # required, Can be None
    lastname: str = ""
    customer_id: str = ""
    country_iso_code: Optional[str] = None

    def build_name(self):
        name = (
            " ".join([self.lastname, self.firstname])
            if self.firstname
            else self.lastname
        )
        name = "{}, {}".format(self.company, name) if self.company else name
        return name

    def build_country(self, sale_channel):
        if self.country_iso_code:
            country = sale_channel.env["res.country"].search(
                [("code", "=", self.country_iso_code)],
                limit=1,
            )
        else:
            country = sale_channel.default_country_id
        return country

    def odoo_model_dump(self, mirakl_channel):
        country = self.build_country(mirakl_channel)
        return {
            "name": self.build_name(),
            "country_id": country.id,
            "channel_ids": [Command.link(mirakl_channel.channel_id.id)],
            "is_from_mirakl": True,
        }
