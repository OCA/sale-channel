from odoo import api, fields, models

from .sale_channel import MIRAKL


class SaleChannelOwner(models.AbstractModel):
    _inherit = "sale.channel.owner"

    sale_channel_external_code = fields.Char(
        compute="_compute_external_code",
        store=True,
    )
    sale_channel_sync_date = fields.Datetime(
        compute="_compute_sync_date",
        store=True,
        help="Date of last import sync for the related record",
    )
    is_from_mirakl = fields.Boolean(
        compute="_compute_is_from_mirakl",
        store=True,
    )

    def _get_values_for_updating(self, field_name):
        """
        :param field_name: field to update
        :param only_single_result: set to True if we want the values to
        come from only one channel default = False
        :return: dictionary containing parameter update values on the calling object
        """
        relation = self._fields.get("channel_ids").relation
        if not relation:
            return {}
        model_name = relation.replace("_", "%")
        models_candidate = self.env["ir.model"].search([("model", "ilike", model_name)])
        model = fields.first(
            models_candidate.filtered(lambda m, r=relation: m.env[m.model]._table == r)
        )
        if model:
            TargetModel = self.env[model.model]
            relation_fields = [
                k
                for k, f in TargetModel._fields.items()
                if f.comodel_name == self._name
            ]
            if relation_fields and len(relation_fields) == 1:
                relation_field = relation_fields[0]
                domain = [
                    (relation_field, "in", self.ids),
                    (field_name, "!=", False),
                ]
                result = TargetModel.read_group(
                    domain,
                    fields=[relation_field, f"{field_name}s:array_agg({field_name})"],
                    groupby=[relation_field],
                )
                values_for_updating = {
                    x[relation_field][0]: x.get(f"{field_name}s", []) for x in result
                }

                return values_for_updating

    @api.depends("channel_ids")
    def _compute_external_code(self):
        """
        Allows to update 'sale_channel_external_code' on the odoo record
        """
        field_name = "sale_channel_external_code"
        self.update({field_name: False})

        values_for_updating = self._get_values_for_updating(field_name)
        if values_for_updating:
            for record in self:
                record.sale_channel_external_code = ", ".join(
                    values_for_updating.get(record.id, [])
                )

    @api.depends("channel_ids")
    def _compute_sync_date(self):
        """
        Allows to update 'sale_channel_sync_date' on the odoo record
        """
        field_name = "sale_channel_sync_date"
        self.update({field_name: False})

        values_for_updating = self._get_values_for_updating(field_name)
        if values_for_updating:
            for record in self:
                record.sale_channel_sync_date = values_for_updating.get(record.id)[0]

    @api.depends("channel_ids")
    def _compute_is_from_mirakl(self):
        for record in self:
            if any(x.channel_type == MIRAKL for x in record.channel_ids):
                record.is_from_mirakl = True
