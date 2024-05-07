from pydantic import BaseModel


class MiraklImportMapper(BaseModel):
    _identity_key = None
    _odoo_model = None

    def get_key(self):
        return getattr(self, self._identity_key, "")
