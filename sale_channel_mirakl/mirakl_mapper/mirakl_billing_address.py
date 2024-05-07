from .mirakl_import_mapper import MiraklImportMapper
from .mirakl_partner_address import MiraklPartnerAddress


class MiraklBillingAddress(MiraklImportMapper, MiraklPartnerAddress):

    customer_notification_email: str = ""
