#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)


from typing import Dict, List

from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    fastapi_endpoint_id,
    odoo_env,
)

from ..models.schemas import SaleCancelInput, SaleImportInput

sale_import_api_router = APIRouter()

# TODO this endpoint are badly named and params are weird
# we should create new clean endpoint and deprecate this one
# when all customer will be migrated we can drop them


@sale_import_api_router.post(
    "/sale/create",
    dependencies=[Depends(authenticated_partner)],
)
async def create(
    params: SaleImportInput,
    endpoint_id: int = Depends(fastapi_endpoint_id),  # noqa: B008
    env: Environment = Depends(odoo_env),  # noqa: B008
) -> List[int]:  # noqa: B008
    """Create all the chunk with the data of sale order.
    Sale order will be created in async with the chunk data.

    Returns a list of chunk info with only id
    """
    endpoint = env["fastapi.endpoint"].sudo().browse(endpoint_id)
    chunks = (
        env["sale.import.service.sale"]
        .with_context(channel_id=endpoint.channel_id.id)
        .create_chunk(params.model_dump()["sale_orders"])
    )
    return chunks.ids


@sale_import_api_router.post(
    "/sale/cancel",
    dependencies=[Depends(authenticated_partner)],
)
async def cancel(
    vals: SaleCancelInput,
    endpoint_id: int = Depends(fastapi_endpoint_id),  # noqa: B008
    env: Environment = Depends(odoo_env),  # noqa: B008
) -> Dict:  # noqa: B008
    """Cancel a sale order based on it's name"""
    endpoint = env["fastapi.endpoint"].sudo().browse(endpoint_id)
    env["sale.import.service.sale"].with_context(
        channel_id=endpoint.channel_id.id
    ).cancel(vals.sale_name)
    return {"success": True}
