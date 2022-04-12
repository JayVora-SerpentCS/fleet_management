# See LICENSE file for full copyright and licensing details.
"""Vehicle Change History."""

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import date_utils


class VehicleChangeHistory(models.TransientModel):
    """Vehicle Change History."""

    _name = 'vehicle.change.history'
    _description = 'Vehicle Change History'

    fleet_id = fields.Many2one('fleet.vehicle', string='Vehicle-ID')
    date_from = fields.Date(string='Date From', default=date_utils.start_of(datetime.now(), 'month'))
    date_to = fields.Date(string='Date To', default=date_utils.end_of(datetime.now(), 'month'))
    report_type = fields.Selection([('engine_history', 'Engine History'),
                                    ('color_history',
                                     'Color History'), ('tire_history', 'Tire History'),
                                    ('battery_history', 'Battery History')], default='color_history')

    def print_report(self):
        """Method to print report."""
        for rec in self:
            if not rec.date_from and not rec.date_to:
                raise UserError(_("User Error!\n 'Please select criteria "
                                "to create Vehicle Change History Report!"))
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise UserError(_("User Error!\n Date To' must "
                                "be greater than 'Date From'!"))
            data = {
                'form': {'date_from': rec.date_from or False,
                         'date_to': rec.date_to or False,
                         'fleet_id': rec.fleet_id and rec.fleet_id.id or False,
                         'report': rec.report_type, }
            }
            return self.env.ref(
                'fleet_operations.action_report_vehicle_change_history').\
                report_action(self, data=data, config=False)
