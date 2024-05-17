from .mirakl_import_mapper import MiraklImportMapper
from .mirakl_partner_address import MiraklPartnerAddress


class MiraklBillingAddress(MiraklImportMapper, MiraklPartnerAddress):

    customer_notification_email: str = ""

    def build_country(self, sale_channel):
        country = sale_channel.default_country_id
        return country
