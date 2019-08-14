# See LICENSE file for full copyright and licensing details.
"""Continue Pending Report."""

from odoo import models


class ContinuePendingRepair(models.TransientModel):
    """Continue Pending Repair."""

    _name = 'continue.pending.repair'
    _description = 'Vehicle Continue Pending Repair'
