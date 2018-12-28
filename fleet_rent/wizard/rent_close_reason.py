# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import models, fields, api


class WizardRentCloseReason(models.TransientModel):
    _name = 'rent.close.reason'
    _description = 'Rent Closing Reason'

    reason = fields.Char(string='Reason', required=True)

    @api.multi
    def close_rent(self):
        if self._context.get('active_id', False) and \
                    self._context.get('active_model', False):
            for reason in self.env[self._context['active_model']].browse(
                                self._context.get('active_id', False)):
                reason.write({'state': 'close',
                              'duration_cover': self.reason,
                              'date_cancel': date.today(),
                              'cancel_by_id': self._uid})
        return True
