# See LICENSE file for full copyright and licensing details.
"""Repair Line Summary."""

from odoo import _, api, fields, models
from odoo.exceptions import Warning


class RepairLineSummary(models.TransientModel):
    """Repair Line Summary."""

    _name = 'repair.line.summary'
    _description = 'Repair Line Summary'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    @api.multi
    def print_report(self):
        """Print Report."""
        for rec in self:
            if rec.date_from > rec.date_to:
                raise Warning(_("User Error!\n'Date To' must be \
                                greater than 'Date From' !"))
            data = {
                'form': {
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                },
            }
            return self.env.ref(
                'fleet_operations.action_report_repair_line_summary').\
                report_action(self, data=data, config=False)
