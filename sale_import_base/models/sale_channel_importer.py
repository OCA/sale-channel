#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from .schemas import SaleOrder


class SaleChannelImporter(models.TransientModel):
    _name = "sale.channel.importer"
    _description = "Sale Channel Importer"

    chunk_id = fields.Many2one("queue.job.chunk", "Chunk")

    def _get_formatted_data(self):
        """Override if you need to translate the Chunk's raw data into the current
        SaleOrder schemas"""
        return self.chunk_id._get_data()

    def _get_existing_so(self, data):
        ref = data["name"]
        return self.env["sale.order"].search(
            [
                ("client_order_ref", "=", ref),
                ("sale_channel_id", "=", self.chunk_id.reference.id),
            ]
        )

    def _manage_existing_so(self, existing_so, data):
        """Override if you need to update existing Sale Order instead of raising
        an error"""
        raise ValidationError(
            _("Sale Order {} has already been created").format(data["name"])
        )

    def run(self):
        # Get validated sale order
        formatted_data = self._get_formatted_data()
        data = SaleOrder(**formatted_data).model_dump()
        existing_so = self._get_existing_so(data)
        if existing_so:
            self._manage_existing_so(existing_so, data)
            return existing_so

        so_vals = self._prepare_sale_vals(data)
        sale_order = self.env["sale.order"].create(so_vals)
        so_line_vals = self._prepare_sale_line_vals(data, sale_order)
        self.env["sale.order.line"].create(so_line_vals)
        self._finalize(sale_order, data)
        return sale_order

    def _prepare_sale_vals(self, data):
        channel = self.chunk_id.reference
        partner = self._process_partner(data["address_customer"])
        address_invoice, address_shipping = self._process_addresses(
            partner, data["address_invoicing"], data["address_shipping"]
        )
        so_vals = {
            "partner_id": partner.id,
            "partner_invoice_id": address_invoice.id,
            "partner_shipping_id": address_shipping.id,
            "client_order_ref": data["name"],
            "sale_channel_id": channel.id,
            "pricelist_id": data.get("pricelist_id") or channel.pricelist_id.id,
            "team_id": channel.crm_team_id.id,
        }

        amount = data.get("amount")
        if amount:
            so_vals.update(
                {
                    "si_amount_total": amount.get("amount_total", 0),
                    "si_amount_untaxed": amount.get("amount_untaxed", 0),
                    "si_amount_tax": amount.get("amount_tax", 0),
                }
            )
        invoice = data.get("invoice")
        if invoice:
            so_vals.update(
                {
                    "si_force_invoice_date": invoice.get("date"),
                    "si_force_invoice_number": invoice.get("number"),
                }
            )
        if channel.internal_naming_method == "client_order_ref":
            so_vals["name"] = data["name"]
        if data.get("date_order"):
            so_vals["date_order"] = data["date_order"]
        return so_vals

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
        channel = self.chunk_id.reference
        external_id = customer_data["external_id"]
        binding = self.env["sale.channel.partner"].search(
            [
                ("external_id", "=", external_id),
                ("sale_channel_id", "=", channel.id),
            ]
        )
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
                        _("Missing State %(state_code)s for country %(country_name)s")
                        % {
                            "state_code": data["state_code"],
                            "country_name": country.name,
                        }
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
        channel = self.chunk_id.reference
        company_id = channel.company_id

        product = self.env["product.product"].search(
            [
                ("default_code", "=", line_data["product_code"]),
                ("product_tmpl_id.company_id", "=", company_id.id),
            ]
        )
        if not product:
            product = self.env["product.product"].search(
                [
                    ("default_code", "=", line_data["product_code"]),
                    ("product_tmpl_id.company_id", "=", False),
                ]
            )
        if not product:
            raise ValidationError(
                _(
                    "There is no active product with the Internal Reference %(code)s "
                    "and related to the company %(company)s."
                )
                % {"code": line_data["product_code"], "company": company_id.name}
            )
        elif len(product) > 1:
            raise ValidationError(
                _("%(product_num)s products found for the code %(code)s.")
                % {"product_num": len(product), "code": line_data["product_code"]}
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

        return vals

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
        provider = self.env["payment.provider"].search([("ref", "=", pmt_data["mode"])])
        if not provider:
            raise ValidationError(
                _("Missing Provider with code {}").format(pmt_data["mode"])
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
                        "Payment currency %(currency)s differs from the "
                        "Sale Order pricelist currency %(pricelist_currency)s"
                    )
                    % {
                        "currency": currency.name,
                        "pricelist_currency": sale_order.currency_id.name,
                    }
                )
        country = (
            sale_order.partner_invoice_id.country_id.id
            or sale_order.partner_id.country_id.id
        )
        payment_vals = {
            "partner_id": sale_order.partner_id.id,
            "provider_id": provider.id,
            "state": "done",
            "last_state_change": fields.Datetime.now(),
            "amount": pmt_data["amount"],
            "fees": 0.00,
            "reference": pmt_data["reference"],
            "provider_reference": pmt_data.get("provider_reference"),
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
                "sale_channel_id": self.chunk_id.reference.id,
                "partner_id": partner.id,
            }
        )
