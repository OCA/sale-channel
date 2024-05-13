from pydantic import BaseModel


class Mirakl(BaseModel):
    _odoo_id = None
    _odoo_model = None

    def _define_internal_id(self, internal_id):
        self._odoo_id = internal_id

    def _get_internal_id(self):
        if self._odoo_id is not None:
            return self._odoo_id
        return NotImplementedError("Not initialized first!")


class MiraklImportMapper(Mirakl):
    _identity_key = None

    def get_key(self):
        return getattr(self, self._identity_key, "")
