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
        except MarshmallowValidationError:
            raise ValidationError(MarshmallowValidationError)
        data = so_datamodel_load.dump()
        so_vals = self._prepare_vals(data)
        new_sale_order = self.env["sale.order"].create(so_vals)
        self._finalize(new_sale_order, data)
        return new_sale_order

    def _prepare_vals(self, data):
        partner = self._process_partner(data)
        address_invoice, address_shipping = self._process_addresses(
            partner, data["address_invoicing"], data["address_shipping"]
        )
        so_vals = {
            "partner_id": partner.id,
            "partner_invoice_id": address_invoice.id,
            "partner_shipping_id": address_shipping.id,
            "si_amount_total": data["amount"]["amount_total"],
            "si_amount_untaxed": data["amount"]["amount_untaxed"],
            "si_amount_tax": data["amount"]["amount_tax"],
            "order_line": [
                (0, 0, self._prepare_sale_line(line)) for line in data["lines"]
            ],
            "sale_channel_id": self.collection.record_id,
        }
        result = self._execute_onchanges(so_vals)
        return result

    def _process_partner(self, data):
        partner = self._find_partner(data)
        vals = self._extract_address_info(data["address_customer"])
        if partner:
            partner.write(vals)
            result = partner
        else:
            result = self.env["res.partner"].create(vals)
            self.env["sale.channel.partner"].create(
                {
                    "external_id": data["address_customer"].get("external_id")
                    or result.email,
                    "sale_channel_id": self.collection.record_id,
                    "partner_id": result.id,
                }
            )
        return result

    def _find_partner(self, data):
        external_id = data["address_customer"].get("external_id")
        binding = self.env["sale.channel.partner"].search(
            [
                ("external_id", "=", external_id),
                ("sale_channel_id", "=", self.collection.record_id),
            ]
        )
        sale_channel = self.env["sale.channel"].browse(self.collection.record_id)
        if binding:
            return binding.partner_id
        elif sale_channel.allow_match_on_email:
            partner = self.env["res.partner"].search(
                [("email", "=", data["address_customer"]["email"])]
            )
            if partner:
                self.env["sale.channel.partner"].create(
                    {
                        "external_id": partner.email,
                        "sale_channel_id": self.collection.record_id,
                        "partner_id": partner.id,
                    }
                )
                return partner

    def _extract_address_info(self, data):
        result = {
            "name": data.get("name") or data.get("email") or data.get("city"),
            "street": data.get("street"),
            "street2": data.get("street2"),
            "zip": data.get("zip"),
            "city": data.get("city"),
            "email": data.get("email"),
        }
        if data.get("state_code"):
            state = self.env["res.country.state"].search(
                [("code", "=", data["state_code"])]
            )
            result["state_id"] = state.id
        if data.get("country_code"):
            country = self.env["res.country"].search(
                [("code", "=", data["country_code"])]
            )
            result["country_id"] = country.id
        return result

    def _process_addresses(self, partner, addr_invoice, addr_shipping):
        # invoice and shipping: find or create partner based on values
        result = []
        for addr in ((addr_invoice, "invoice"), (addr_shipping, "delivery")):
            vals = self._extract_address_info(addr[0])
            vals["type"] = addr[1]
            addr_virtual = self.env["res.partner"].new(vals)
            # on create res.partner Odoo rewrites address values to be the
            # same as the parent's, thus we force set to our values
            for k, v in vals.items():
                setattr(addr_virtual, k, v)
            addr_virtual["parent_id"] = partner.id
            version = addr_virtual.get_address_version()
            result.append(version)
        return result

    def _prepare_sale_line(self, line_data):
        product_id = (
            self.env["product.product"]
            .search([("default_code", "=", line_data["product_code"])])
            .id
        )
        qty = line_data["qty"]
        price_unit = line_data["price_unit"]
        discount = line_data["discount"]
        result = {
            "product_id": product_id,
            "product_uom_qty": qty,
            "price_unit": price_unit,
            "discount": discount,
        }
        description = line_data.get("description")
        if description:
            result["name"] = line_data.get("description")
        return result

    def _execute_onchanges(self, so_vals):
        onchange_fields = [
            "payment_mode_id",
            "workflow_process_id",
            "fiscal_position_id",
            "partner_id",
            "partner_shipping_id",
            "partner_invoice_id",
        ]
        so_vals_onchanged = self.env["sale.order"].play_onchanges(
            so_vals, onchange_fields
        )
        # we need a virtual SO for onchanges on the order lines
        # because their onchanges depend on parent's values
        virtual_so = self.env["sale.order"].new(so_vals_onchanged)
        line_vals = so_vals["order_line"]
        for line in line_vals:
            line[2]["order_id"] = virtual_so
        line_vals_onchanged = [
            self.env["sale.order.line"].play_onchanges(line[2], ["product_id"])
            for line in line_vals
        ]
        lines_onchanged_commands = [(0, 0, val) for val in line_vals_onchanged]
        so_vals_onchanged["order_line"] = lines_onchanged_commands
        return so_vals_onchanged

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
