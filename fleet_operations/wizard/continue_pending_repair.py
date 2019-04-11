# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models


class ContinuePendingRepair(models.TransientModel):
    _name = 'continue.pending.repair'
    _description = 'Vehicle Continue Pending Repair'
