# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.api import Environment
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.depends import (
    authenticated_partner_impl,
    fastapi_endpoint_id,
    odoo_env,
)

from ..controllers.main import sale_import_api_router


# TODO improve
# In fact we do not really need to hack the partner impl
# what we really want is just to check the authentification (in our case the api key)
def api_key_based_authenticated_partner_impl(
    api_key: str = Depends(  # noqa: B008
        APIKeyHeader(
            name="api-key",
            description="In this demo, you can use a user's login as api key.",
        )
    ),
    _id: int = Depends(fastapi_endpoint_id),  # noqa: B008
    env: Environment = Depends(odoo_env),  # noqa: B008
) -> Partner:
    key = env["auth.api.key"].with_user(SUPERUSER_ID)._retrieve_api_key(api_key)
    endpoint = env["fastapi.endpoint"].sudo().browse(_id)
    if not key or key.user_id != endpoint.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key"
        )
    return key.user_id.partner_id


class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("sale_import", "Sale Import")],
        ondelete={"sale_import": "cascade"},
    )
    sale_import_auth_method = fields.Selection(
        selection=[("api_key", "Api Key")],
        string="Authenciation method",
    )
    channel_id = fields.Many2one("sale.channel", "Channel")

    def _get_fastapi_routers(self) -> List[APIRouter]:
        if self.app == "sale_import":
            return [sale_import_api_router]
        return super()._get_fastapi_routers()

    @api.constrains("app", "demo_auth_method")
    def _valdiate_demo_auth_method(self):
        for rec in self:
            if rec.app == "sale_import" and not rec.sale_import_auth_method:
                raise ValidationError(
                    _(
                        "The authentication method is required for app %(app)s",
                        app=rec.app,
                    )
                )

    @api.model
    def _fastapi_app_fields(self) -> List[str]:
        fields = super()._fastapi_app_fields()
        fields.append("sale_import_auth_method")
        return fields

    def _get_app(self):
        app = super()._get_app()
        if self.app == "sale_import":
            app.dependency_overrides[
                authenticated_partner_impl
            ] = api_key_based_authenticated_partner_impl
        return app
