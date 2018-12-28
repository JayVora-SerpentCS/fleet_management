# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import models, fields, api


class WizardWritOffCancelReason(models.TransientModel):
    _name = 'writeoff.cancel.reason'
    _description = 'Vehicle Write-off Cancel Reason'

    reason = fields.Char(string='Reason', required=True)

    @api.multi
    def cancel_writoff(self):
        if self._context.get('active_id', False) and \
                    self._context.get('active_model', False):
            for reason in self.env[self._context['active_model']].browse(
                                self._context.get('active_id', False)):
                if reason.vehicle_id:
                    reason.vehicle_id.write({'state': 'inspection',
                                             'last_change_status_date':
                                             date.today()})
                reason.write({'cancel_note': self.reason,
                              'state': 'cancel', 'date_cancel': date.today(),
                              'cancel_by_id': self._uid
                              })
        return True