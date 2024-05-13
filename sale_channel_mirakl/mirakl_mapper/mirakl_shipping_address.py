from .country_builder import CountryBuilder
from .mirakl_import_mapper import MiraklImportMapper
from .mirakl_partner_address import MiraklPartnerAddress


class MiraklShippingAddress(MiraklImportMapper, MiraklPartnerAddress, CountryBuilder):

    additional_info: str
    shipping_zone_code: str = ""

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
