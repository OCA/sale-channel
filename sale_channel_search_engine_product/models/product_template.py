# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "sale.channel.owner"]
    _name = "product.template"

    count_se_binding_total = fields.Integer(compute="_compute_count_binding")
    count_se_binding_done = fields.Integer(compute="_compute_count_binding")
    count_se_binding_pending = fields.Integer(compute="_compute_count_binding")
    count_se_binding_error = fields.Integer(compute="_compute_count_binding")

    def _compute_count_binding(self):
        res = self.with_context(
            active_test=False
        ).product_variant_ids._get_count_per_state()
        for record in self:
            done = pending = error = 0
            for variant in record.with_context(active_test=False).product_variant_ids:
                done += res[variant.id]["done"]
                pending += res[variant.id]["pending"]
                error += res[variant.id]["error"]
            record.count_se_binding_done = done
            record.count_se_binding_pending = pending
            record.count_se_binding_error = error
            record.count_se_binding_total = done + pending + error

    def _on_sale_channel_modified(self):
        self.product_variant_ids._synchronize_channel_index()

    def open_se_binding(self):
        return self.with_context(
            active_test=False
        ).product_variant_ids.open_se_binding()
