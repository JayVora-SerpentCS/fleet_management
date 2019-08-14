# See LICENSE file for full copyright and licensing details.
"""Rent Close Reason ."""


from datetime import date

from odoo import api, fields, models


class WizardRentCloseReason(models.TransientModel):
    """Wizard Rent Close Reason Model."""

    _name = 'rent.close.reason'
    _description = 'Rent Closing Reason'

    reason = fields.Char(string='Reason', required=True)

    @api.multi
    def close_rent(self):
        """Method to close rent."""
        if self._context.get('active_id', False) and \
                self._context.get('active_model', False):
            for reason in self.env[self._context['active_model']].browse(
                    self._context.get('active_id', False)):
                reason.write({'state': 'close',
                              'duration_cover': self.reason,
                              'date_cancel': date.today(),
                              'cancel_by_id': self._uid})
        return True
