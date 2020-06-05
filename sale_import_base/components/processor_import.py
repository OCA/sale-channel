#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.addons.component.core import AbstractComponent


# DISCUSSION: abstractcomponent?
class ProcessorImport(AbstractComponent):
    _name = "processor.import"
    _inherit = "processor"
    _usage = "import"
