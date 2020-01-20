# See LICENSE file for full copyright and licensing details.
"""Vehicle Change History."""


from datetime import date, datetime

from odoo import api, fields, models
from odoo.tools import ustr


class WizardWritOffCancelReason(models.TransientModel):
    """Wizard Writeoff Cancel Reason."""

    _name = 'writeoff.cancel.reason'
    _description = 'Vehicle Write-off Cancel Reason'

    reason = fields.Char(string='Reason', required=True)

    def cancel_writoff(self):
        """Method Cancel Writeoff."""
        if self._context.get('active_id', False) and \
                self._context.get('active_model', False):
            user = self.env.user
            line = '---------------------------------------------------------'
            line += '--------------------------'
            notes = 'Your vehicle Write-off is Cancelled by' + \
                " " + user.name + \
                " " + 'on' + " " + ustr(datetime.now().date())
            writeoff_rec = self.env[self._context['active_model']].\
                browse(self._context['active_id'])
            for wiz in self:
                if writeoff_rec.vehicle_id:
                    writeoff_rec.vehicle_id.write({
                        'state': 'inspection',
                        'last_change_status_date': date.today()
                    })
                writeoff_rec.write({
                    'cancel_note': notes + '\n' + line + '\n' + wiz.reason,
                    'state': 'cancel', 'date_cancel': date.today(),
                    'cancel_by_id': user and user.id or False
                })
