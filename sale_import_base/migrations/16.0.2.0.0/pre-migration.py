# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_tables(env.cr, [("queue_job_chunk", "sale_import_payload")])
    openupgrade.rename_models(env.cr, [("queue.job.chunk", "sale.import.payload")])
    # Module update will take care of constraint and everything.
    env.cr.execute(
        """ALTER TABLE sale_import_payload RENAME COLUMN record_id to sale_channel_id"""
    )
