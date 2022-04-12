# See LICENSE file for full copyright and licensing details.
"""Vehicle Change History."""

from odoo import api, fields, models
from odoo.tools import ustr, format_date


class WizardWritOffCancelReason(models.TransientModel):
    """Wizard Write off Cancel Reason."""

    _name = 'writeoff.cancel.reason'
    _description = 'Vehicle Write-off Cancel Reason'

    reason = fields.Char(string='Reason', required=True)

    def cancel_writoff(self):
        """Method Cancel Write off."""
        if self._context.get('active_id', False) and \
                self._context.get('active_model', False):
            user = self.env.user
            line = '---------------------------------------------------------'
            line += '--------------------------'
            notes = 'Your vehicle Write-off is Cancelled by' + \
                " " + user.name + \
                " " + 'on' + " " + ustr(format_date(self.env, fields.Date.today(),
                                                    self.env.user.lang, date_format=False))
            writeoff_rec = self.env[self._context['active_model']].\
                browse(self._context['active_id'])
            for wiz in self:
                if writeoff_rec.vehicle_id:
                    writeoff_rec.vehicle_id.write({
                        'state': 'inspection',
                        'last_change_status_date': fields.Date.today()
                    })
                writeoff_rec.write({
                    'cancel_note': notes + '\n' + line + '\n' + wiz.reason,
                    'state': 'cancel', 'date_cancel': fields.Date.today(),
                    'cancel_by_id': user and user.id or False
                })
