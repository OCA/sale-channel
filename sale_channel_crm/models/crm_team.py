#  Copyright (c) Trescloud 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class CrmTeam(models.Model):
    _inherit = ["crm.team", "sale.channel.owner"]
    _name = "crm.team"
