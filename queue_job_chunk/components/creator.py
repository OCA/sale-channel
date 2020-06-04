#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import json

from odoo.addons.component.core import Component


class Creator(Component):
    """ Just creates a record with given vals """

    _inherit = "base"
    _name = "basic.creator"
    _collection = "queue.job.chunk"
    _usage = "basic_create"

    def run(self, data):
        data = json.loads(data)
        return self.model.create(data)
