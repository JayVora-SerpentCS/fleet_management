# See LICENSE file for full copyright and licensing details.
"""Fleet Model."""

import logging

from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class FleetVehicleExtend(models.Model):
    """Fleet Vehicle Extend."""

    _inherit = 'fleet.vehicle'

    @api.multi
    def _count_rent(self):
        """Count the total number of Rent for the current vehicle."""
        rent_obj = self.env['fleet.rent']
        for vehicle in self:
            vehicle.rent_count = \
                rent_obj.search_count([('vehicle_id', '=', vehicle.id)])

    # income_acc_id = fields.Many2one("account.account",
    #                                 string="Income Account")
    # expence_acc_id = fields.Many2one("account.account",
    #                                  string="Expense Account")
    rent_count = fields.Integer(compute='_count_rent',
                                string="Rents")
