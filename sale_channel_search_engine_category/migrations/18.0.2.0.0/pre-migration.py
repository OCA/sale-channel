# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # Root categories were always published before this version:
    # keep this behaviour for existing channels. The column is created
    # here so the ORM does not initialize it with the field default.
    cr.execute(
        """
        ALTER TABLE sale_channel
        ADD COLUMN IF NOT EXISTS should_publish_root BOOLEAN
        """
    )
    cr.execute("UPDATE sale_channel SET should_publish_root = TRUE")
