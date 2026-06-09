# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    old_chunk_group = env.ref("queue_job_chunk.group_queue_job_chunk_user")
    new_payload_group = env.ref("sale_import_base.group_sale_import_payload")
    new_payload_group.write({"users": [(6, 0, old_chunk_group.users.ids)]})
