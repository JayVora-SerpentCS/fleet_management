# See LICENSE file for full copyright and licensing details.
"""Repair Line Summary."""

from odoo import _, api, fields, models
from odoo.exceptions import Warning
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF
import calendar


class RepairLineSummary(models.TransientModel):
    """Repair Line Summary."""

    _name = 'repair.line.summary'
    _description = 'Repair Line Summary'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    @api.model
    def default_get(self, default_fields):
        """Method used to set default start and end date."""
        res = super(RepairLineSummary, self).default_get(default_fields)
        curr_month = datetime.today().month
        curr_year = datetime.today().year
        last_day = calendar.monthrange(curr_year, curr_month)[1]
        start_date = date(curr_year, curr_month, 1)
        end_date = date(curr_year, curr_month, last_day)
        res.update({'date_from': datetime.strftime(start_date, DSDF),
                    'date_to': datetime.strftime(end_date, DSDF)})
        return res

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
