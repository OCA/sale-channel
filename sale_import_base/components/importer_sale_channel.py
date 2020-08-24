#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from marshmallow_objects import ValidationError as MarshmallowValidationError

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ImporterSaleChannel(Component):
    _inherit = "processor"
    _name = "importer.sale.channel"
    _apply_on = ["sale.order"]
    _usage = "json_import"

    def run(self):
        try:
            so_datamodel_load = self.env.datamodels["sale.order"].load_json(
                self.collection.data_str
            )
        except MarshmallowValidationError as e:
            raise ValidationError(e)
        data = so_datamodel_load.dump()
        errors = self.run_validators(data)
        if any([val for field, val in errors.items()]):
            raise ValidationError(
                _("Validation error on one or mode fields: %s") % str(errors)
            )
        so_vals = self._prepare_sale_vals(data)
        sale_order = self.env["sale.order"].create(so_vals)
        so_line_vals = self._prepare_sale_line_vals(data, sale_order)
        self.env["sale.order.line"].create(so_line_vals)
        self._finalize(sale_order, data)
        return sale_order

    def run_validators(self, data):
        """ Runs all the validations against in-db data """
        errors = {}
        for addr in ("address_customer", "address_shipping", "address_invoicing"):
            self._validate_address(data[addr], errors)
        for line in data["lines"]:
            self._validate_line(line, errors)
        if data.get("payment"):
            self._validate_payment(data["payment"], errors)
        return errors

    def _validate_address(self, address, all_errors):
        if not all_errors.get("address"):
            all_errors["address"] = list()
        errors = []
        if address.get("country_code"):
            country = self.env["res.country"].search(
                [("code", "=", address["country_code"])]
            )
            if len(country.ids) != 1:
                errors += [_("Could not determine one country from country code")]
        if address.get("state_code"):
            state = self.env["res.country.state"].search(
                [
                    ("code", "=", address["state_code"]),
                    ("country_id", "in", country and country.ids),
                ]
            )
            if len(state.ids) != 1:
                errors += [_("Could not determine one state from state code")]
        all_errors["address"] += errors

    def _validate_line(self, line, all_errors):
        if not all_errors.get("lines"):
            all_errors["lines"] = list()
        product = self.env["product.product"].search(
            [("default_code", "=", line["product_code"])]
        )
        if len(product.ids) != 1:
            all_errors["lines"] += [
                _("Could not find one product with the product code: {}").format(
                    line["product_code"]
                )
            ]

    def _validate_payment(self, payment, all_errors):
        errors = []
        acquirer = self.env["payment.acquirer"].search([("name", "=", payment["mode"])])
        if not acquirer:
            errors += [_("No payment type found for given mode")]

        if payment.get("currency_code"):
            currency_id = self.env["res.currency"].search(
                [("name", "=", payment["currency_code"])]
            )
            if not currency_id:
                errors += [_("No currency type found for given code")]
        all_errors["payment"] = errors

    def _prepare_sale_vals(self, data):
        partner = self._process_partner(data["address_customer"])
        address_invoice = self._process_address(
            partner, data["address_invoicing"], "invoice"
        )
        address_shipping = self._process_address(
            partner, data["address_shipping"], "delivery"
        )
        channel = self.env["sale.channel"].browse(self.collection.record_id)
        so_vals = {
            "name": data["name"],
            "partner_id": partner.id,
            "partner_invoice_id": address_invoice.id,
            "partner_shipping_id": address_shipping.id,
            "si_amount_total": data.get("amount", {}).get("amount_total", 0),
            "si_amount_untaxed": data.get("amount", {}).get("amount_untaxed", 0),
            "si_amount_tax": data.get("amount", {}).get("amount_tax", 0),
            "si_force_invoice_date": data.get("invoice") and data["invoice"]["date"],
            "si_force_invoice_number": data.get("invoice")
            and data["invoice"]["number"],
            "sale_channel_id": channel.id,
            "pricelist_id": data.get("pricelist_id") or channel.pricelist_id.id,
        }
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

    def _prepare_partner(self, data):
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
        if data.get("country_code"):
            country = self.env["res.country"].search(
                [("code", "=", data["country_code"])]
            )
            result["country_id"] = country.id
        if data.get("state_code"):
            state = self.env["res.country.state"].search(
                [
                    ("code", "=", data["state_code"]),
                    ("country_id", "in", [data.get("country_id")]),
                ]
            )
            result["state_id"] = state.id
        return result

    def _process_address(self, partner, address, address_type):
        vals = self._prepare_partner(address)
        vals.update({"partner_id": partner.id, "type": address_type})
        addr_virtual = self.env["res.partner"].new(vals)
        return addr_virtual.get_address_version()

    def _prepare_sale_line_vals(self, data, sale_order):
        return [self._prepare_sale_line(line, sale_order) for line in data["lines"]]

    def _prepare_sale_line(self, line_data, sale_order):
        product_id = (
            self.env["product.product"]
            .search([("default_code", "=", line_data["product_code"])])
            .id
        )
        vals = {
            "product_id": product_id,
            "product_uom_qty": line_data["qty"],
            "price_unit": line_data["price_unit"],
            "discount": line_data.get("discount"),
            "order_id": sale_order.id,
        }
        if line_data.get("description"):
            vals["name"] = line_data["description"]
        return self.env["sale.order.line"].play_onchanges(vals, ["product_id"])

    def _finalize(self, new_sale_order, raw_import_data):
        """ Extend to add final operations """
        self._create_payment(new_sale_order, raw_import_data)

    def _create_payment(self, sale_order, data):
        if not data.get("payment"):
            return
        pmt_data = data["payment"]
        acquirer_name = pmt_data["mode"]
        acquirer = self.env["payment.acquirer"].search([("name", "=", acquirer_name)])
        payment_vals = {
            "partner_id": sale_order.partner_id.id,
            "acquirer_id": acquirer.id,
            "type": "server2server",
            "state": "done",
            "amount": pmt_data["amount"],
            "fees": 0.00,
            "reference": pmt_data["reference"],
            "acquirer_reference": pmt_data.get("acquirer_reference"),
            "sale_order_ids": [(4, sale_order.id, 0)],
            "currency_id": sale_order.currency_id.id,
        }
        self.env["payment.transaction"].create(payment_vals)

    def _binding_partner(self, partner, external_id):
        self.env["sale.channel.partner"].create(
            {
                "external_id": external_id,
                "sale_channel_id": self.collection.record_id,
                "partner_id": partner.id,
            }
        )
