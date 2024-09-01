# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        partner_id = cls.env.ref("base.res_partner_2")
        sale_channel_id = cls.env.ref("sale_channel.sale_channel_amazon")
        model_id = cls.env["ir.model"].search([("model", "=", "sale.order")])
        template_id = cls.env.ref("sale.mail_template_sale_confirmation")
        picking_template_id = cls.env.ref(
            "stock.mail_template_data_delivery_confirmation"
        )
        product_id = cls.env.ref("sale.product_product_4e")
        picking_model_id = cls.env["ir.model"].search([("model", "=", "stock.picking")])
        sale_channel_id.write(
            {
                "notification_ids": [
                    (
                        0,
                        0,
                        {
                            "notification_type": "sale_confirmation",
                            "model_id": model_id.id,
                            "template_id": template_id.id,
                        },
                    )
                ]
            }
        )

        cls.order_id = cls.env["sale.order"].create(
            {
                "partner_id": partner_id.id,
                "sale_channel_id": sale_channel_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        sale_channel_id.write(
            {
                "notification_ids": [
                    (
                        0,
                        0,
                        {
                            "notification_type": "sale_confirmation",
                            "model_id": model_id.id,
                            "template_id": template_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "picking_shipped",
                            "model_id": picking_model_id.id,
                            "template_id": picking_template_id.id,
                        },
                    ),
                ]
            }
        )
