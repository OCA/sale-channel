from odoo import api, fields, models


class MiraklBinding(models.AbstractModel):
    _name = "mirakl.binding"
    _description = "used to attache several items to mirakl sale channel"

    is_from_mirakl = fields.Boolean()
    # mirakl_code = fields.Char(
    #     compute="_compute_mirakl_code",
    #     store=True,
    # )
    sync_date = fields.Datetime(
        compute="_compute_sync_date",
        store=True,
    )

    @api.depends("channel_ids")
    def _compute_mirakl_code(self):
        self._fields.get("channel_ids").relation
        # Check there is a (Odoo) model related to this relation table
        model_name = ""
        TargetModel = self.env[model_name]
        relation_fields = [
            f for f in TargetModel._fields.values() if f.comodel_name == self._name
        ]
        self.update({"mirakl_code": False})
        if relation_fields and len(relation_fields) == 1:
            relation_field = relation_fields[0]
            domain = [
                (relation_field.name, "in", self.ids),
                ("mirakl_code", "!=", False),
            ]
            result = TargetModel.read_group(
                domain,
                fields=[relation_field.name, "mirakl_codes:array_agg(mirakl_code)"],
                groupby=[relation_field.name],
            )
            records_mirakl_code = {
                x[relation_field.name][0]: x.get("mirakl_codes", "")
                for x in result
                if x.get("__count", 0) == 1
            }
            for record in self:
                record.mirakl_code = records_mirakl_code.get(record.id, "")

    @api.depends("channel_ids")
    def _compute_sync_date(self):
        self.update({"sync_date": False})
