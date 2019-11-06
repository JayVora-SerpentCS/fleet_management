# See LICENSE file for full copyright and licensing details.
"""Fleet Rent and Account related model."""

from datetime import datetime
from odoo import api, fields, models
from odoo.tools import ustr


class AccountInvoice(models.Model):
    """Account Invoice Model."""

    _inherit = "account.invoice"

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 help='Vehicle Name.')
    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle')
    is_deposit_inv = fields.Boolean(string="Is Deposit Invoice")
    is_deposit_return_inv = fields.Boolean(string="Is Deposit Return Invoice")

    @api.multi
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        refund_vals = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
        refund_vals.update({
            'fleet_rent_id': self.fleet_rent_id and self.fleet_rent_id.id or False,
            })
        return refund_vals

    @api.multi
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

    @api.multi
    def action_invoice_open(self):
        """Method to Change state in Open."""
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            record = self.env['tenancy.rent.schedule'].search([('invc_id', '=', invoice.id)])
            record.write({'state': 'open'})
        return res


class AccountMoveLine(models.Model):
    """Account Move Line Model."""

    _inherit = "account.move.line"

    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle')


class account_abstract_payment(models.AbstractModel):
    """Account Abstract Model."""

    _inherit = 'account.abstract.payment'

    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        """Overridden Method to update deposit amount in payment wizard."""
        rec = super(account_abstract_payment, self).\
            _compute_payment_amount(invoices, currency)
        if self._context.get('active_model', False) == 'fleet.rent':
            return self._context.get('default_amount' or 0.0)
        return rec


class AccountPayment(models.Model):
    """Account Payment Model."""

    _inherit = 'account.payment'

    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle',
                                    help='Rental Vehicle Name')

    def _create_payment_entry(self, amount):

        res = super(AccountPayment, self)._create_payment_entry(amount)
        res.line_ids.write({
            'fleet_rent_id': self.fleet_rent_id and self.fleet_rent_id.id or False,
            })
        return res

    @api.multi
    def post(self):
        """Overridden Method to update tenancy infromation."""
        inv_obj = self.env['account.invoice']
        rent_sched_obj = self.env['tenancy.rent.schedule']
        if self._context.get('active_ids', False):
            for invoice in inv_obj.browse(self._context['active_ids']):
                if invoice.fleet_rent_id:
                    self.write({
                        'fleet_rent_id': invoice.fleet_rent_id and
                        invoice.fleet_rent_id.id or False
                    })
        res = super(AccountPayment, self).post()
        user = self.env.user
        notes = 'Your Rent Payment is Registered by' + " " + user.name + \
            " " + 'on' + " " + ustr(datetime.now().date())
        for invoice in self.invoice_ids:
            for rent_line in rent_sched_obj.search([
                    ('invc_id', '=', invoice and invoice.id or False)]):
                tenancy_vals = {'pen_amt': 0.0}
                if rent_line.invc_id:
                    tenancy_vals.update({
                        'pen_amt': rent_line.invc_id.residual or 0.0
                    })
                    if rent_line.invc_id.state == 'paid':
                        tenancy_vals.update({
                            'paid': True,
                            'move_check': True,
                            'state': 'paid',
                            'note': notes,
                        })
                rent_line.write(tenancy_vals)
            if self._context.get('active_model', False) and \
                    self._context['active_model'] == 'account.invoice':
                for inv in inv_obj.browse(self._context['active_ids']):
                    if inv.fleet_rent_id and inv.is_deposit_return_inv:
                        inv.fleet_rent_id.write({
                            'is_deposit_return': True,
                            'amount_return': inv.amount_total - inv.residual or 0.0
                        })
        return res
