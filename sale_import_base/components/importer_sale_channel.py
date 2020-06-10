#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from marshmallow_objects import ValidationError as MarshmallowValidationError

from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ImporterSaleChannel(Component):
    _inherit = "processor"
    _name = "importer.sale.channel"
    _apply_on = ["sale.order"]
    _usage = "json_import"

    def run(self, raw_data):
        """
        :param raw_data: json-like string
        :return: generated sale order
        """
        # we need this step because the chunk data is stored as
        # a string (so we can edit it)
        try:
            so_datamodel_load = self.env.datamodels["sale.order"].load_json(raw_data)
        except MarshmallowValidationError as e:
            raise ValidationError(e)
        data = so_datamodel_load.dump()
        so_vals = self._prepare_sale_vals(data)
        sale_order = self.env["sale.order"].create(so_vals)
        so_line_vals = self._prepare_sale_line_vals(data, sale_order)
        self.env["sale.order.line"].create(so_line_vals)
        self._finalize(sale_order, data)
        return sale_order

    def _prepare_sale_vals(self, data):
        partner = self._process_partner(data)
        address_invoice = self._process_address(
            partner, data["address_invoicing"], "invoice"
        )
        address_shipping = self._process_address(
            partner, data["address_shipping"], "delivery"
        )
        so_vals = {
            "partner_id": partner.id,
            "partner_invoice_id": address_invoice.id,
            "partner_shipping_id": address_shipping.id,
            "si_amount_total": data["amount"]["amount_total"],
            "si_amount_untaxed": data["amount"]["amount_untaxed"],
            "si_amount_tax": data["amount"]["amount_tax"],
            "sale_channel_id": self.collection.record_id,
        }
        onchange_fields = [
            "payment_mode_id",
            "workflow_process_id",
            "fiscal_position_id",
            "partner_id",
            "partner_shipping_id",
            "partner_invoice_id",
        ]
        return self.env["sale.order"].play_onchanges(so_vals, onchange_fields)

    def _process_partner(self, data):
        partner = self._find_partner(data["address_customer"])
        vals = self._prepare_partner(data["address_customer"])
        if partner:
            partner.write(vals)
            return partner
        else:
            partner = self.env["res.partner"].create(vals)
            self._binding_partner(partner, data["address_customer"]["external_id"])
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
            "street": data["street"],
            "street2": data.get("street2"),
            "zip": data["zip"],
            "city": data["city"],
            "email": data.get("email"),
        }
        if data.get("state_code"):
            state = self.env["res.country.state"].search(
                [("code", "=", data["state_code"])]
            )
            result["state_id"] = state.id
        country = self.env["res.country"].search([("code", "=", data["country_code"])])
        result["country_id"] = country.id
        return result

    def _process_address(self, partner, address, address_type):
        vals = self._prepare_partner(address)
        addr_virtual = self.env["res.partner"].new(vals)
        addr_virtual.parent_id = partner.id
        addr_virtual.type = address_type
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
            "discount": line_data["discount"],
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
            "acquirer_id": acquirer.id,
            "type": "server2server",
            "state": "done",
            "amount": pmt_data["amount"],
            "fees": 0.00,
            "reference": pmt_data["reference"],
            "acquirer_reference": pmt_data["reference"],
            "sale_order_ids": [4, 0, [sale_order.id]],
            "currency_id": sale_order.currency_id.id,
        }
        new_pmt = self.env["payment.transaction"].create(payment_vals)
        sale_order.transaction_ids = new_pmt

    def _binding_partner(self, partner, external_id):
        self.env["sale.channel.partner"].create(
            {
                "external_id": external_id,
                "sale_channel_id": self.collection.record_id,
                "partner_id": partner.id,
            }
        )
