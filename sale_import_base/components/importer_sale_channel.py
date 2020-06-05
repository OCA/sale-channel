#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from copy import deepcopy

from marshmallow_objects import ValidationError as MarshmallowValidationError

from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

MAPPINGS_SALE_ORDER_ADDRESS_SIMPLE = [
    "name",
    "street",
    "street2",
    "zip",
    "city",
    "email",
]


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
        except Exception:
            raise
        json_data_initial = so_datamodel_load.dump()
        json_data = deepcopy(json_data_initial)
        so_vals = self._si_process_data(json_data)
        new_sale_order = self.env["sale.order"].create(so_vals)
        self._si_finalize(new_sale_order, json_data_initial)
        return new_sale_order

    # DATAMODEL PROCESSORS
    def _si_process_data(self, so_vals):
        """ Transform values in-place
         to make it usable in create() """
        self._si_process_simple_fields(so_vals)
        self._si_process_m2os(so_vals)
        so_vals = self._si_simulate_onchanges(so_vals)
        return so_vals

    def _si_process_simple_fields(self, so_vals):
        del so_vals["currency_code"]
        del so_vals["payment"]

    def _si_process_m2os(self, so_vals):
        channel_id = self._si_get_channel(so_vals)
        partner_id = self._si_get_partner(so_vals, channel_id)
        self._si_process_addresses(partner_id, so_vals)
        self._si_process_lines(so_vals)
        self._si_process_amount(so_vals)
        self._si_process_invoice(so_vals)
        self._si_process_sale_channel(so_vals)

    def _si_get_channel(self, so_vals):
        sale_channel = self.env["sale.channel"].search(
            [("name", "=", so_vals["sale_channel"])]
        )
        return sale_channel

    def _si_get_partner(self, so_vals, sale_channel):
        external_id = so_vals["address_customer"].get("external_id")
        binding = self.env["sale.channel.partner"].search(
            [
                ("external_id", "=", external_id),
                ("sale_channel_id", "=", sale_channel.id),
            ]
        )
        if binding:
            return binding.partner_id
        if sale_channel.allow_match_on_email:
            partner = self.env["res.partner"].search(
                [("email", "=", so_vals["address_customer"]["email"])]
            )
            if partner:
                return partner
        return self._si_create_partner(so_vals)

    def _si_create_partner(self, so_vals):
        partner_vals = dict()
        for field in MAPPINGS_SALE_ORDER_ADDRESS_SIMPLE:
            partner_vals[field] = so_vals["address_customer"][field]
        country = self.env["res.country"].search(
            [("code", "=", so_vals["address_customer"]["country_code"])]
        )
        partner_vals["country_id"] = country.id
        partner = self.env["res.partner"].create(partner_vals)
        return partner

    def _si_process_addresses(self, partner_id, so_vals):
        # customer itself
        vals_addr_customer = so_vals["address_customer"]
        new_state = (
            self.env["res.country.state"]
            .search([("code", "=", vals_addr_customer.get("state_code"))])
            .id
        )
        partner_id.state_id = new_state
        new_country = (
            self.env["res.country"]
            .search([("code", "=", vals_addr_customer["country_code"])])
            .id
        )
        partner_id.country_id = new_country
        for field in MAPPINGS_SALE_ORDER_ADDRESS_SIMPLE:
            new_val = vals_addr_customer.get(field)
            if new_val:
                setattr(partner_id, field, new_val)
        so_vals["partner_id"] = partner_id.id
        del so_vals["address_customer"]

        # invoice and shipping: find or create partner based on values
        res_partner_obj = self.env["res.partner"]
        vals_addr_invoicing = so_vals["address_invoicing"]
        vals_addr_shipping = so_vals["address_shipping"]
        for address_field in (
            (vals_addr_shipping, "partner_shipping_id", "address_shipping", "delivery"),
            (vals_addr_invoicing, "partner_invoice_id", "address_invoicing", "invoice"),
        ):
            addr = address_field[0]
            field = address_field[1]
            vals_key = address_field[2]
            type_di = address_field[3]
            if addr.get("state_code"):
                addr["state_id"] = self.env["res.country.state"].search(
                    [("code", "=", addr.get("state_code"))]
                )
                del addr["state_code"]
            addr["country_id"] = self.env["res.country"].search(
                [("code", "=", addr["country_code"])]
            )
            del addr["country_code"]
            addr["parent_id"] = partner_id
            addr["type"] = type_di
            res_partner_virtual = res_partner_obj.new(addr)
            # on create res.partner Odoo rewrites address values to be the
            # same as the parent's, thus we force set to our values
            for k, v in addr.items():
                setattr(res_partner_virtual, k, v)
            version = res_partner_virtual.get_address_version()
            version.active = True
            so_vals[field] = version.id
            del so_vals[vals_key]

    def _si_process_lines(self, so_vals):
        lines = so_vals["lines"]
        so_vals["order_line"] = list()
        for line in lines:
            product_id = (
                self.env["product.product"]
                .search([("default_code", "=", line["product_code"])])
                .id
            )
            qty = line["qty"]
            price_unit = line["price_unit"]
            description = line.get("description") or None
            discount = line["discount"]
            line_vals_dict = {
                "product_id": product_id,
                "product_uom_qty": qty,
                "price_unit": price_unit,
                "name": description,
                "discount": discount,
            }
            line_vals_command = (0, 0, line_vals_dict)
            so_vals["order_line"].append(line_vals_command)
        del so_vals["lines"]

    def _si_process_amount(self, so_vals):
        for k, v in so_vals["amount"].items():
            si_key = "si_" + k
            so_vals[si_key] = v
        del so_vals["amount"]

    def _si_process_invoice(self, so_vals):
        # TODO actually use that val
        del so_vals["invoice"]

    def _si_process_sale_channel(self, so_vals):
        channel = self.env["sale.channel"].search(
            [("name", "=", so_vals.get("sale_channel"))]
        )
        if channel:
            so_vals["sale_channel_id"] = channel.id
            del so_vals["sale_channel"]

    def _si_simulate_onchanges(self, order):
        """ Drawn from connector_ecommerce module with modifications:
        onchange fields, some syntax
        Play the onchange of the sales order and it's lines
        :param order: sales order values
        :type: dict
        :param order_lines: data of the sales order lines
        :type: list of dict
        :return: the sales order updated by the onchanges
        :rtype: dict
        """
        order_onchange_fields = [
            "partner_id",
            "partner_shipping_id",
            "payment_mode_id",
            "workflow_process_id",
            "fiscal_position_id",
        ]

        line_onchange_fields = ["product_id"]

        # play onchange on sales order
        order = self._si_simulate_onchanges_play_onchanges(
            "sale.order", order, order_onchange_fields
        )

        # play onchange on sales order line
        processed_order_lines = []
        line_lists = [order["order_line"]]

        for line_list in line_lists:
            for idx, command_line in enumerate(line_list):
                # line_list format:[(0, 0, {...}), (0, 0, {...})]
                if command_line[0] in (0, 1):  # create or update values
                    # keeps command number and ID (or 0)
                    old_line_data = deepcopy(command_line[2])
                    # give a virtual order_id for the fiscal position/taxes
                    old_line_data["order_id"] = self.env["sale.order"].new(order)
                    new_line_data = self._si_simulate_onchanges_play_onchanges(
                        "sale.order.line", old_line_data, line_onchange_fields
                    )
                    del new_line_data["order_id"]
                    new_line = (command_line[0], command_line[1], new_line_data)
                    processed_order_lines.append(new_line)
                    # in place modification of the sales order line in the list
                    line_list[idx] = new_line
        return order

    def _si_simulate_onchanges_play_onchanges(self, model, values, onchange_fields):
        model = self.env[model]
        onchange_specs = model._onchange_spec()

        # we need all fields in the dict even the empty ones
        # otherwise 'onchange()' will not apply changes to them
        all_values = values.copy()
        for field in model._fields:
            if field not in all_values:
                all_values[field] = False

        # we work on a temporary record
        new_record = model.new(all_values)

        new_values = {}
        for field in onchange_fields:
            onchange_values = new_record.onchange(all_values, field, onchange_specs)
            new_values_diff = self._si_simulate_onchanges_get_new_values(
                values, onchange_values, model=model._name
            )
            new_values.update(new_values_diff)
            all_values.update(new_values)

        res = {f: v for f, v in all_values.items() if f in values or f in new_values}
        return res

    def _si_simulate_onchanges_get_new_values(
        self, record, on_change_result, model=None
    ):
        vals = on_change_result.get("value", {})
        new_values = {}
        for fieldname, value in vals.items():
            if not record.get(fieldname):  # fieldname not in record:
                if model:
                    column = self.env[model]._fields[fieldname]
                    if column.type == "many2one":
                        value = value[0]  # many2one are tuple (id, name)
                new_values[fieldname] = value
        return new_values

    # FINALIZERS
    def _si_finalize(self, new_sale_order, raw_import_data):
        """ Extend to add final operations """
        self._si_sync_binding(new_sale_order, raw_import_data)
        self._si_create_payment(new_sale_order, raw_import_data)

    def _si_sync_binding(self, sale_order, data):
        if not data["address_customer"].get("external_id"):
            return
        existing_binding = self.env["sale.channel.partner"].search(
            [
                ("sale_channel_id", "=", sale_order.sale_channel_id.id),
                ("partner_id", "=", sale_order.partner_id.id),
            ]
        )
        if not existing_binding:
            binding_vals = {
                "sale_channel_id": sale_order.sale_channel_id.id,
                "partner_id": sale_order.partner_id.id,
                "external_id": data["address_customer"]["external_id"],
            }
            self.env["sale.channel.partner"].create(binding_vals)

    def _si_create_payment(self, sale_order, data):
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

    def helper_find_binding(self, sale_channel, external_id):
        binding = self.env["sale.channel.partner"].search(
            [
                ("external_id", "=", external_id),
                ("sale_channel_id", "=", sale_channel.id),
            ]
        )
        return binding
