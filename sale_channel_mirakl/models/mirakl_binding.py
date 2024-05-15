from odoo import api, fields, models

from .sale_channel_owner import SaleChannelOwner


class MiraklBinding(models.AbstractModel):
    _name = "mirakl.binding"
    _description = "used to attache several items to mirakl sale channel"

    is_from_mirakl = fields.Boolean()
    mirakl_code = fields.Char(
        compute="_compute_mirakl_code",
        store=True,
    )
    sync_date = fields.Datetime(
        compute="_compute_sync_date",
        store=True,
        help="Date of last import sync for the related record",
    )

    def _get_values_for_updating(self, field_name, only_single_result=False):
        """
        :param field_name: field to update
        :param only_single_result: set to True if we want the values to
        come from only one channel default = False
        :return:
        """
        relation = None
        if SaleChannelOwner._name in self._inherit:
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
                if only_single_result:
                    values_for_updating = {
                        x[relation_field][0]: x.get(f"{field_name}s", [])
                        for x in result
                        if x.get(relation_field + "_count", 0) == 1
                    }
                else:
                    values_for_updating = {
                        x[relation_field][0]: x.get(f"{field_name}s", [])
                        for x in result
                    }

                return values_for_updating

    @api.depends("channel_ids")
    def _compute_mirakl_code(self):
        field_name = "mirakl_code"
        self.update({field_name: False})

        values_for_updating = self._get_values_for_updating(field_name)
        for record in self:
            record.mirakl_code = ", ".join(values_for_updating.get(record.id, []))

    @api.depends("channel_ids")
    def _compute_sync_date(self):
        field_name = "sync_date"
        self.update({field_name: False})

        values_for_updating = self._get_values_for_updating(
            field_name, only_single_result=True
        )
        for record in self:
            if values_for_updating.get(record.id):
                record.sync_date = values_for_updating.get(record.id)[0]
