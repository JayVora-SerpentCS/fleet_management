# See LICENSE file for full copyright and licensing details.
"""Rent Close Reason ."""


from datetime import datetime, date

from odoo import api, fields, models
from odoo.tools import ustr


class WizardRentCloseReason(models.TransientModel):
    """Wizard Rent Close Reason Model."""

    _name = 'rent.close.reason'
    _description = 'Rent Closing Reason'

    reason = fields.Text(string='Reason')

    @api.multi
    def close_rent(self):
        """Method to close rent."""
        user = self.env.user
        date = datetime.now().date()
        notes = 'Your Rent Payment is Cancelled by' + " " + user.name + \
                " " + 'on' + " " + ustr(date)
        if self._context.get('active_id', False) and \
                self._context.get('active_model', False):
            for rent in self.env[self._context['active_model']].browse(
                    self._context.get('active_id', False)):
                tenancy_obj = self.env['tenancy.rent.schedule'].search([('state', 'in', ['draft', 'open']), ('fleet_rent_id', '=', rent.id)])
                tenancy_obj.write({'state': 'cancel',
                                    'note': notes})
                rent.write({'state': 'close',
                            'close_reson': self.reason,
                            'date_close': date.today(),
                            'rent_close_by': self._uid})
        return True
