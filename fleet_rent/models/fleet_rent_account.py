# See LICENSE file for full copyright and licensing details.
"""Fleet Rent and Account related model."""

from odoo import fields, models
from odoo.tools import ustr, format_date


class AccountInvoice(models.Model):
    """Account Invoice Model."""

    _inherit = "account.move"

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 help='Vehicle Name.')
    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle')
    is_deposit_inv = fields.Boolean(string="Is Deposit Invoice")
    is_deposit_return_inv = fields.Boolean(string="Is Deposit Return Invoice")

    def _prepare_refund(self, invoice, invoice_date=None, date=None,
                        description=None, journal_id=None):
        refund_vals = super(AccountInvoice, self)._prepare_refund(
            invoice, invoice_date, date, description, journal_id)
        refund_vals.update({
            'fleet_rent_id': self.fleet_rent_id and
            self.fleet_rent_id.id or False,
        })
        return refund_vals

    def action_move_create(self):
        """Method Action Move Create."""
        res = super(AccountInvoice, self).action_move_create()
        for inv_rec in self:
            if inv_rec.move_id and inv_rec.vehicle_id:
                inv_rec.move_id.write({
                    'asset_id': inv_rec.vehicle_id.id or False,
                    'ref': 'Maintenance Invoice',
                    'source': inv_rec.vehicle_id.name or False
                })
        return res

    def action_invoice_open(self):
        """Method to Change state in Open."""
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            record = self.env['tenancy.rent.schedule'].search(
                [('invc_id', '=', invoice.id)])
            record.write({'state': 'open'})
        return res


class AccountMoveLine(models.Model):
    """Account Move Line Model."""

    _inherit = "account.move.line"

    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle')


class AccountPayment(models.AbstractModel):
    """Account Abstract Model."""

    _inherit = 'account.payment'

    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle',
                                    help='Rental Vehicle Name')

    # def _compute_payment_amount(self, invoices=None, currency=None):
    def _compute_payment_amount(self, invoices, currency, journal, date):
        """Overridden Method to update deposit amount in payment wizard."""
        rec = super(AccountPayment, self).\
            _compute_payment_amount(invoices, currency, journal, date)
        if self._context.get('active_model', False) == 'fleet.rent':
            return self._context.get('default_amount' or 0.0)
        return rec


class AccountPaymentRegister(models.TransientModel):
    """Inherit Account Payment Register."""

    _inherit = "account.payment.register"

    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle',
                                    help='Rental Vehicle Name')

    def _create_payment_vals_from_wizard(self):
        res = super(AccountPaymentRegister,
                    self)._create_payment_vals_from_wizard()
        res.update({'fleet_rent_id': self.fleet_rent_id and
                    self.fleet_rent_id.id or False, })
        return res

    def _create_payments(self):
        """Overridden Method to update tenancy information."""
        inv_obj = self.env['account.move']
        rent_sched_obj = self.env['tenancy.rent.schedule']
        if self._context.get('active_ids', False):
            for invoice in inv_obj.browse(self._context['active_ids']):
                if invoice.fleet_rent_id:
                    self.write({
                        'fleet_rent_id': invoice.fleet_rent_id and
                        invoice.fleet_rent_id.id or False
                    })
        res = super(AccountPaymentRegister, self)._create_payments()
        user = self.env.user
        notes = 'Your Rent Payment is Registered by' + " " + user.name + \
            " " + 'on' + " " + ustr(format_date(self.env, fields.Date.today(),
                                    self.env.user.lang, date_format=False))
        if self._context.get('active_model', False) and\
                self._context['active_model'] == 'account.move' and\
                self._context.get('active_ids', False):
            for move in inv_obj.browse(self._context['active_ids']):
                for rent_line in rent_sched_obj.search([
                        ('invc_id', '=', move.id)]):
                    tenancy_vals = {'pen_amt': 0.0}
                    if rent_line.invc_id:
                        tenancy_vals.update({
                            'pen_amt': rent_line.invc_id.amount_residual or 0.0
                        })
                        if rent_line.invc_id.state == 'posted':
                            tenancy_vals.update({
                                'paid': True,
                                'move_check': True,
                                'state': 'paid',
                                'note': notes,
                            })
                    rent_line.write(tenancy_vals)
                if move.fleet_rent_id and move.is_deposit_return_inv:
                    move.fleet_rent_id.write({
                        'is_deposit_return': True,
                        'amount_return':
                        move.amount_total - move.amount_residual or 0.0
                    })
        return res
