# See LICENSE file for full copyright and licensing details.
"""Vehicle Change History."""

from odoo import _, api, fields, models

from odoo.exceptions import Warning


class VehicleChangeHistory(models.TransientModel):
    """Vehicle Change History."""

    _name = 'vehicle.change.history'
    _description = 'Vehicle Change History'

    fleet_id = fields.Many2one('fleet.vehicle', string='Vehicle-ID')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    @api.multi
    def print_report(self):
        """Method to print report."""
        for rec in self:
            if not rec.date_from and not rec.date_to and not rec.fleet_id:
                raise Warning(_("User Error!\n 'Please select criteria \
                         to create Vehicle Change History Report!"))
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise Warning(_("User Error!\n Date To' must \
                            be greater than 'Date From'!"))
            data = {
                'form': {'date_from': rec.date_from or False,
                         'date_to': rec.date_to or False,
                         'fleet_id': rec.fleet_id and rec.fleet_id.id or False}
            }
            return self.env.ref(
                'fleet_operations.action_report_vehicle_change_history').\
                report_action(self, data=data, config=False)
