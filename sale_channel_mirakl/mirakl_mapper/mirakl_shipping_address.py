from .mirakl_import_mapper import MiraklImportMapper
from .mirakl_partner_address import MiraklPartnerAddress


class MiraklShippingAddress(MiraklImportMapper, MiraklPartnerAddress):

    additional_info: str
    shipping_zone_code: str = ""
