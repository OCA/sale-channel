#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from marshmallow_objects import ValidationError as MarshmallowValidationError

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ImporterSaleChannel(Component):
    _inherit = "processor"
    _name = "importer.sale.channel"
    _apply_on = ["sale.order"]
    _usage = "json_import"

    def _get_existing_so(self, data):
        ref = data["name"]
        channel_id = self.collection.record_id
        return self.env["sale.order"].search(
            [("client_order_ref", "=", ref), ("sale_channel_id", "=", channel_id)]
        )

    def _run(self, data):
        try:
            so_datamodel_load = self.env.datamodels["sale.order"].load_json(data)
        except MarshmallowValidationError as e:
            raise ValidationError(e)
        data = so_datamodel_load.dump()
        existing_so = self._get_existing_so(data)
        if existing_so:
            raise ValidationError(
                _("Sale Order {} has already been created").format(data["name"])
            )
        so_vals = self._prepare_sale_vals(data)
        sale_order = self.env["sale.order"].create(so_vals)
        so_line_vals = self._prepare_sale_line_vals(data, sale_order)
        self.env["sale.order.line"].create(so_line_vals)
        self._finalize(sale_order, data)
        return sale_order

    def run(self):
        return self._run(self.collection.data_str)

    def _prepare_sale_vals(self, data):
        partner = self._process_partner(data["address_customer"])
        address_invoice, address_shipping = self._process_addresses(
            partner, data["address_invoicing"], data["address_shipping"]
        )
        channel = self.env["sale.channel"].browse(self.collection.record_id)
        so_vals = {
            "partner_id": partner.id,
            "partner_invoice_id": address_invoice.id,
            "partner_shipping_id": address_shipping.id,
            "si_amount_total": data.get("amount", {}).get("amount_total", 0),
            "si_amount_untaxed": data.get("amount", {}).get("amount_untaxed", 0),
            "si_amount_tax": data.get("amount", {}).get("amount_tax", 0),
            "si_force_invoice_date": data.get("invoice") and data["invoice"]["date"],
            "si_force_invoice_number": data.get("invoice")
            and data["invoice"]["number"],
            "client_order_ref": data["name"],
            "sale_channel_id": channel.id,
            "pricelist_id": data.get("pricelist_id") or channel.pricelist_id.id,
        }
        if channel.internal_naming_method == "client_order_ref":
            so_vals["name"] = data["name"]
        if data.get("date_order"):
            so_vals["date_order"] = data["date_order"]
        onchange_fields = [
            "payment_mode_id",
            "workflow_process_id",
            "fiscal_position_id",
            "partner_id",
            "partner_shipping_id",
            "partner_invoice_id",
        ]
        result = self.env["sale.order"].play_onchanges(so_vals, onchange_fields)
        return result

    def _process_partner(self, customer_data):
        partner = self._find_partner(customer_data)
        vals = self._prepare_partner(customer_data)
        if partner:
            partner.write(vals)
            return partner
        else:
            partner = self.env["res.partner"].create(vals)
            self._binding_partner(partner, customer_data["external_id"])
            return partner

    def _find_partner(self, customer_data):
        external_id = customer_data["external_id"]
        binding = self.env["sale.channel.partner"].search(
            [
                ("external_id", "=", external_id),
                ("sale_channel_id", "=", self.collection.record_id),
            ]
        )
        channel = self.collection.reference
        if binding:
            return binding.partner_id
        elif channel.allow_match_on_email:
            partner = self.env["res.partner"].search(
                [("email", "=", customer_data["email"])]
            )
            if partner:
                self._binding_partner(partner, customer_data["external_id"])
                return partner

    def _prepare_partner(self, data, parent_id=None, archived=None):
        result = {
            "name": data["name"],
            "street": data.get("street"),
            "street2": data.get("street2"),
            "zip": data.get("zip"),
            "city": data.get("city"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "mobile": data.get("mobile"),
        }
        if parent_id:
            result["parent_id"] = parent_id
        if archived:
            result["active"] = False
        if data.get("country_code"):
            country = self.env["res.country"].search(
                [("code", "=", data["country_code"])]
            )
            if not country:
                raise ValidationError(
                    _("Missing country {}").format(data["country_code"])
                )
            result["country_id"] = country.id
            if data.get("state_code"):
                state = self.env["res.country.state"].search(
                    [("code", "=", data["state_code"]), ("country_id", "=", country.id)]
                )
                if not state:
                    raise ValidationError(
                        _("Missing State {} for country {}").format(
                            data["state_code"], country.name
                        )
                    )
                result["state_id"] = state.id
        return result

    def _process_addresses(self, parent, address_invoice, address_shipping):
        vals_addr_invoice = self._prepare_partner(address_invoice, parent.id, True)
        vals_addr_shipping = self._prepare_partner(address_shipping, parent.id, True)
        if vals_addr_invoice == vals_addr_shipping:
            # not technically correct for the shipping addr, but this shouldn't matter
            vals_addr_invoice["type"] = "invoice"
            result = self.env["res.partner"].create(vals_addr_invoice)
            return (result, result)
        else:
            vals_addr_invoice["type"] = "invoice"
            vals_addr_shipping["type"] = "delivery"
            return (
                self.env["res.partner"].create(vals_addr_invoice),
                self.env["res.partner"].create(vals_addr_shipping),
            )

    def _prepare_sale_line_vals(self, data, sale_order):
        return [self._prepare_sale_line(line, sale_order) for line in data["lines"]]

    def _prepare_sale_line(self, line_data, sale_order):
        product = self.env["product.product"].search(
            [("default_code", "=", line_data["product_code"])]
        )
        if not product:
            raise ValidationError(
                _("Missing product {}").format(line_data["product_code"])
            )
        elif len(product) > 1:
            raise ValidationError(
                _("{} products found for the code {}").format(
                    len(product), line_data["product_code"]
                )
            )
        vals = {
            "product_id": product.id,
            "product_uom_qty": line_data["qty"],
            "price_unit": line_data["price_unit"],
            "discount": line_data.get("discount"),
            "order_id": sale_order.id,
        }
        if line_data.get("description"):
            vals["name"] = line_data["description"]
        return self.env["sale.order.line"].play_onchanges(vals, ["product_id"])

    def _finalize(self, new_sale_order, raw_import_data):
        """Extend to add final operations"""
        channel = new_sale_order.sale_channel_id
        if channel.confirm_order:
            new_sale_order.action_confirm()
        if channel.invoice_order:
            new_sale_order._create_invoices()
        self._create_payment(new_sale_order, raw_import_data)

    def _create_payment(self, sale_order, data):
        if not data.get("payment"):
            return
        pmt_data = data["payment"]
        acquirer = self.env["payment.acquirer"].search(
            [("code", "=", pmt_data["mode"])]
        )
        if not acquirer:
            raise ValidationError(
                _("Missing Acquirer with code {}").format(pmt_data["mode"])
            )
        if pmt_data.get("currency_code"):
            currency = self.env["res.currency"].search(
                [("name", "=", pmt_data["currency_code"])]
            )
            if not currency:
                raise ValidationError(
                    _("Missing currency {}").format(pmt_data["currency_code"])
                )
            if currency != sale_order.currency_id:
                raise ValidationError(
                    _(
                        "Payment currency {} differs from the "
                        "Sale Order pricelist currency {}"
                    ).format(currency.name, sale_order.currency_id.name)
                )
        country = (
            sale_order.partner_invoice_id.country_id.id
            or sale_order.partner_id.country_id.id
        )
        payment_vals = {
            "partner_id": sale_order.partner_id.id,
            "acquirer_id": acquirer.id,
            "type": "server2server",
            "state": "done",
            "date": datetime.now(),
            "amount": pmt_data["amount"],
            "fees": 0.00,
            "reference": pmt_data["reference"],
            "acquirer_reference": pmt_data.get("acquirer_reference"),
            "sale_order_ids": [(4, sale_order.id, 0)],
            "currency_id": sale_order.currency_id.id,
            "partner_country_id": country,
            "invoice_ids": [(6, 0, sale_order.invoice_ids.ids)],
        }
        return self.env["payment.transaction"].create(payment_vals)

    def _binding_partner(self, partner, external_id):
        self.env["sale.channel.partner"].create(
            {
                "external_id": external_id,
                "sale_channel_id": self.collection.record_id,
                "partner_id": partner.id,
            }
        )
