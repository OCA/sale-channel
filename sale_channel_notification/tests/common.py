# Copyright 2026 Akretion (http://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo.tests.common import RecordCapturer, TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.sale_channel_1 = cls.env.ref("sale_channel.sale_channel_amazon")
        cls.sale_channel_2 = cls.env.ref("sale_channel.sale_channel_ebay")
        cls.template_1 = cls.env.ref("sale.mail_template_sale_confirmation")
        product = cls.env.ref("sale.product_product_4e")

        cls.sale_channel_1.write(
            {
                "custom_notifications": True,
                "notification_ids": [
                    (
                        0,
                        0,
                        {
                            "notification_type": "sale_confirmation",
                            "template_id": cls.template_1.id,
                        },
                    )
                ],
            }
        )

        cls.order_id = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "sale_channel_id": cls.sale_channel_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        cls.default_capture_domain = [
            ("model", "=", "sale.order"),
            ("res_id", "=", cls.order_id.id),
        ]

    @contextmanager
    def capture_mails_messages(self, domain=None):
        domain = domain or self.default_capture_domain
        with (
            RecordCapturer(self.env["mail.mail"], domain) as mails,
            RecordCapturer(self.env["mail.message"], domain) as messages,
        ):
            yield mails, messages
