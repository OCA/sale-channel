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
        country = sale_channel.default_country_id
        if self.shipping_zone_code:
            country = (
                sale_channel.env["res.country"].search(
                    [("code", "=", self.shipping_zone_code)],
                    limit=1,
                )
                or country
            )
        return country

    def odoo_model_dump(self, mirakl_channel):
        """
        Allows you to build an odoo record
        :param mirakl_channel: Mirakl channel on which the partner is attached
        :return: dictionary allowing to construct the odoo record corresponding
         to the data coming from mirakl
        """
        country = self.build_country(mirakl_channel)
        return {
            "name": self.build_name(),
            "country_id": country.id,
            "channel_ids": [Command.link(mirakl_channel.channel_id.id)],
            "is_from_mirakl": True,
        }
