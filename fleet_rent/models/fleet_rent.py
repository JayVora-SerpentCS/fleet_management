# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import re
import threading
from datetime import datetime
from odoo.exceptions import Warning, except_orm, ValidationError
from odoo import models, fields, api, sql_db, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, ustr


class ResPartner(models.Model):
    _inherit = "res.partner"

    tenant = fields.Boolean(string="Is Tenant?")
    tenancy_ids = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='tenant_id',
        string='Rental Vehicle Details',
        help='Rental Vehicle Details')
    maintenance_ids = fields.One2many(
        comodel_name='property.maintenance',
        inverse_name='tenant_id',
        string='Maintenance Details')
    doc_name = fields.Char(
        string='Filename')
    id_attachment = fields.Binary(
        string='Identity Proof')

    @api.constrains('mobile')
    def _check_value_tp(self):
        for val in self:
            if val.mobile:
                if re.match("^\+|[1-9]{1}[0-9]{3,14}$", val.mobile) \
                        is not None:
                    pass
                else:
                    raise ValidationError('Please Enter Valid Mobile Number')

    @api.constrains('email')
    def _check_values_tp(self):
        expr = "^[a-zA-Z0-9._+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]*\.*[a-zA-Z]{2,4}$"
        for val in self:
            if val.email:
                if re.match(expr, val.email) is not None:
                    pass
                else:
                    raise ValidationError('Please Enter Valid Email Id')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        help='Vehicle Name.')
    new_tenancy_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Rental Vehicle')

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        for inv_rec in self:
            if inv_rec.move_id and inv_rec.move_id.id:
                inv_rec.move_id.write({'asset_id':
                                       inv_rec.vehicle_id.id or False,
                                       'ref': 'Maintenance Invoice',
                                       'source':
                                       inv_rec.vehicle_id.name or False})
        return res


class RentType(models.Model):
    _name = "rent.type"
    _description = 'Vehicle Rent Type'

    @api.model
    def create(self, vals):
        if vals.get('duration') < 1:
            raise ValidationError("You Can't Enter Duration Less \
                                    Than One(1).")
        return super(RentType, self).create(vals)

    @api.multi
    @api.depends('duration', 'renttype')
    def name_get(self):
        res = []
        for rec in self:
            rec_str = ''
            if rec.duration:
                rec_str += ustr(rec.duration)
            if rec.renttype:
                rec_str += ' ' + rec.renttype
            res.append((rec.id, rec_str))
        return res

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        args += ['|', ('duration', operator, name),
                      ('renttype', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()

    @api.onchange('duration', 'renttype')
    def onchange_renttype_name(self):
        full_name = ''
        for rec in self:
            if rec.duration:
                full_name += ustr(rec.duration)
            if rec.renttype:
                full_name += ' ' + ustr(rec.renttype)
            rec.name = full_name

    name = fields.Char(string="Name")
    duration = fields.Integer(string="Duration", default=1)
    renttype = fields.Selection(
        [('Hours', 'Hours'),
         ('Days', 'Days'),
         ('Weeks', 'Weeks'),
         ('Months', 'Months'),
         ('Years', 'Years')],
        default='Months',
        string='Rent Type')


class MaintenanceType(models.Model):
    _name = 'maintenance.type'
    _description = 'Vehicle Maintenance Type'

    name = fields.Char(
        string='Maintenance Type',
        size=50,
        required=True)
    main_cost = fields.Boolean(
        string='Recurring cost',
        help='Check if the recuring cost involve')
    cost = fields.Float(
        string='Maintenance Cost',
        help='insert the cost')


class MaintenanaceCost(models.Model):
    _name = 'maintenance.cost'
    _description = 'Vehicle Maintenance Cost'

    maint_type = fields.Many2one(
        comodel_name='maintenance.type',
        string='Maintenance Type')
    cost = fields.Float(
        string='Maintenance Cost',
        help='insert the cost')
    tenancy = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Rental Vehicle')

    @api.onchange('maint_type')
    def onchange_property_id(self):
        """
        This Method is used to set maintenance type related fields value,
        on change of property.
        @param self: The object pointer
        """
        if self.maint_type:
            self.cost = self.maint_type.cost or 0.00


class PropertyMaintenace(models.Model):
    _name = "property.maintenance"
    _description = 'Property Maintenance'
    _inherit = ['mail.thread']

    date = fields.Date(
        string='Date',
        default=fields.Date.context_today)
    cost = fields.Float(
        string='Cost')
    type = fields.Many2one(
        comodel_name='maintenance.type',
        string='Type')
    assign_to = fields.Many2one(
        comodel_name='res.partner',
        string='Assign To')
    invc_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')
    renters_fault = fields.Boolean(
        string='Renters Fault',
        default=False,
        copy=True)
    invc_check = fields.Boolean(
        string='Already Created',
        default=False)
    mail_check = fields.Boolean(
        string='Mail Send',
        default=False)
    property_id = fields.Many2one(
        comodel_name='account.asset.asset',
        string='Property')
    account_code = fields.Many2one(
        comodel_name='account.account',
        string='Account Code')
    notes = fields.Text(
        string='Notes',
        size=100)
    name = fields.Selection(
        [('Renew', 'Renew'),
         ('Repair', 'Repair'),
         ('Replace', 'Replace')],
        string='Action',
        default='Repair')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('progress', 'In Progress'),
         ('incomplete', 'Incomplete'),
         ('done', 'Done')],
        string='State',
        default='draft')
    tenant_id = fields.Many2one(
        comodel_name='res.partner',
        string='Tenant')

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

    @api.multi
    def send_maint_mail(self):
        """
        This Method is used to send an email to assigned person.
        @param self: The object pointer
        """
        try:
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid, context = self.env.uid, self.env.context
            with api.Environment.manage():
                self.env = api.Environment(new_cr, uid, context)
                ir_model_data = self.env['ir.model.data']
                try:
                    if self._context.get('cancel'):
                        template_id = ir_model_data.get_object_reference(
                            'property_management',
                            'mail_template_property_maintainance_close')[1]
                    if self._context.get('invoice'):
                        template_id = ir_model_data.get_object_reference(
                            'property_management',
                            'email_template_edi_invoice_id')[1]
                    else:
                        template_id = ir_model_data.get_object_reference(
                            'property_management',
                            'mail_template_property_maintainance')[1]
                except ValueError:
                    template_id = False
                for maint_rec in self:
                    if not maint_rec.property_id.current_tenant_id.email:
                        raise except_orm(
                            ("Cannot send email: Assigned user has no \
                                email address."),
                            maint_rec.property_id.current_tenant_id.name)
                    self.env['mail.template'].browse(template_id).send_mail(
                        maint_rec.id, force_send=True)
        finally:
            self.env.cr.close()

    @api.multi
    def start_maint(self):
        """
        This Method is used to change maintenance state to progress.
        @param self: The object pointer
        """
        self.write({'state': 'progress'})
        thrd_cal = threading.Thread(target=self.send_maint_mail)
        thrd_cal.start()

    @api.multi
    def cancel_maint(self):
        """
        This Method is used to change maintenance state to incomplete.
        @param self: The object pointer
        """
        self.write({'state': 'incomplete'})
        thrd_cal = threading.Thread(target=self.send_maint_mail)
        thrd_cal.start()

    @api.onchange('renters_fault')
    def onchange_renters_fault(self):
        for data in self:
            if data.renters_fault:
                data.tenant_id = \
                    data.property_id.tenancy_property_ids.tenant_id
            else:
                data.tenant_id = 0

    @api.onchange('assign_to')
    def onchanchange_assign(self):
        for data in self:
            data.account_code = data.assign_to.property_account_payable_id

    @api.multi
    def create_invoice(self):
        """
        This Method is used to create invoice from maintenance record.
        @param self: The object pointer
        """
        for data in self:
            if not data.account_code:
                raise Warning(_("Please Select Account Code"))
            if not data.property_id.id:
                raise Warning(_("Please Select Property"))
            tncy_ids = self.env['account.analytic.account'].search(
                [('property_id', '=', data.property_id.id),
                 ('state', '!=', 'close')])
            if len(tncy_ids.ids) == 0:
                raise Warning(_("No current tenancy for this property"))
            else:
                for tenancy_data in tncy_ids:
                    inv_line_values = {
                        'name': 'Maintenance For ' + data.type.name or "",
                        'origin': 'property.maintenance',
                        'quantity': 1,
                        'account_id':
                        data.property_id.income_acc_id.id or False,
                        'price_unit': data.cost or 0.00,
                    }

                    inv_values = {
                        'origin': 'Maintenance For ' + data.type.name or "",
                        'type': 'out_invoice',
                        'property_id': data.property_id.id,
                        'partner_id': tenancy_data.tenant_id.id or False,
                        'account_id': data.account_code.id or False,
                        'invoice_line_ids': [(0, 0, inv_line_values)],
                        'amount_total': data.cost or 0.0,
                        'date_invoice': datetime.now().strftime(
                                    DEFAULT_SERVER_DATE_FORMAT) or False,
                        'number': tenancy_data.name or '',
                    }
                if data.renters_fault:
                    inv_values.update(
                        {'partner_id': tenancy_data.tenant_id.id or False})
                else:
                    inv_values.update(
                        {'partner_id':
                         tenancy_data.property_id.property_manager.id or False
                         })
                acc_id = self.env['account.invoice'].create(inv_values)
                data.write(
                    {'renters_fault': False,
                     'invc_check': True,
                     'invc_id': acc_id.id,
                     'state': 'done'})
        thrd_cal = threading.Thread(target=self.send_maint_mail)
        thrd_cal.start()
        return True

    @api.multi
    def open_invoice(self):
        """
        This Method is used to Open invoice from maintenance record.
        @param self: The object pointer
        """
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }


class CostCost(models.Model):
    _name = "cost.cost"
    _description ="Cost"
    _order = 'date'

    @api.one
    @api.depends('move_id')
    def _get_move_check(self):
        self.move_check = bool(self.move_id)

    date = fields.Date(
        string='Date')
    amount = fields.Float(
        string='Amount')
    name = fields.Char(
        string='Description',
        size=100)
    payment_details = fields.Char(
        string='Payment Details',
        size=100)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Purchase Entry')
    purchase_property_id = fields.Many2one(
        comodel_name='account.asset.asset',
        string='Property')
    remaining_amount = fields.Float(
        string='Remaining Amount',
        help='Shows remaining amount in currency')
    move_check = fields.Boolean(
        compute='_get_move_check',
        method=True,
        string='Posted',
        store=True)
    rmn_amnt_per = fields.Float(
        string='Remaining Amount In %',
        help='Shows remaining amount in Percentage')
    invc_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')

    @api.multi
    def create_invoice(self):
        """
        This button Method is used to create account invoice.
        @param self: The object pointer
        """
        if not self.purchase_property_id.partner_id:
            raise Warning(_('Please Select Partner'))
        if not self.purchase_property_id.expense_account_id:
            raise Warning(_('Please Select Expense Account'))
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'purchase')])

        inv_line_values = {
            'origin': 'Cost.Cost',
            'name': 'Purchase Cost For' + '' + self.purchase_property_id.name,
            'price_unit': self.amount or 0.00,
            'quantity': 1,
            'account_id': self.purchase_property_id.expense_account_id.id,
        }

        inv_values = {
            'payment_term_id':
            self.purchase_property_id.payment_term.id or False,
            'partner_id': self.purchase_property_id.partner_id.id or False,
            'type': 'in_invoice',
            'property_id': self.purchase_property_id.id or False,
            'invoice_line_ids': [(0, 0, inv_line_values)],
            'date_invoice':
            datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT) or False,
            'journal_id': account_jrnl_obj.id or False,
        }
        acc_id = self.env['account.invoice'].create(inv_values)
        self.write({'invc_id': acc_id.id, 'move_check': True})
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_supplier_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    @api.multi
    def open_invoice(self):
        """
        This Method is used to Open invoice
        @param self: The object pointer
        """
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_supplier_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }


class TenancyRentSchedule(models.Model):
    _name = "tenancy.rent.schedule"
    _description = 'Tenancy Rent Schedule'
    _rec_name = "tenancy_id"
    _order = 'start_date'

    @api.one
    @api.depends('move_id')
    def _get_move_check(self):
        self.move_check = bool(self.move_id)

    state = fields.Selection(
        related='tenancy_id.state',
        string='Status')
    note = fields.Text(
        string='Notes',
        help='Additional Notes.')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency')
    amount = fields.Float(
        string='Amount',
        default=0.0,
        currency_field='currency_id',
        help="Rent Amount.")
    start_date = fields.Datetime(
        string='Date',
        help='Start Date.')
    end_date = fields.Date(
        string='End Date',
        help='End Date.')
    cheque_detail = fields.Char(
        string='Cheque Detail',
        size=30)
    move_check = fields.Boolean(
        compute='_get_move_check',
        method=True,
        string='Posted',
        store=True)
    rel_tenant_id = fields.Many2one(
        comodel_name='res.partner',
        string="Tenant")
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Depreciation Entry')
    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        help='Vehicle Name.')
    tenancy_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Rental Vehicle',
        help='Rental Vehicle Name.')
    paid = fields.Boolean(
        string='Paid',
        help="True if this rent is paid by tenant")
    invc_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')
    inv = fields.Boolean(
        string='Invoice')
    pen_amt = fields.Float(
        string='Pending Amount',
        help='Pending Amount.',
        store=True)

    @api.multi
    def create_invoice(self):
        """
        Create invoice for Rent Schedule.
        """
        journal_ids = self.env['account.journal'].search(
            [('type', '=', 'sale')])
        if not self.tenancy_id.vehicle_id.income_acc_id.id:
            raise Warning(_('Please Configure Income Account from Vehicle.'))
        inv_line_main = {
            'origin': 'tenancy.rent.schedule',
            'name': 'Maintenance cost',
            'price_unit': self.tenancy_id.main_cost or 0.00,
            'quantity': 1,
            'account_id': self.tenancy_id.vehicle_id.income_acc_id.id or False,
            'account_analytic_id': self.tenancy_id.id or False,
        }
        if self.tenancy_id.multi_prop:
            for data in self.tenancy_id.prop_id:
                for account in data.property_ids.income_acc_id:
                    inv_line_main.update({'account_id': account.id})

        inv_line_values = {
            'origin': 'tenancy.rent.schedule',
            'name': 'Tenancy(Rent) Cost',
            'price_unit': self.amount or 0.00,
            'quantity': 1,
            'account_id': self.tenancy_id.vehicle_id.income_acc_id.id or False,
            'account_analytic_id': self.tenancy_id.id or False,
        }
        if self.tenancy_id.multi_prop:
            for data in self.tenancy_id.prop_id:
                for account in data.property_ids.income_acc_id:
                    inv_line_values.update({'account_id': account.id})
        inv_values = {
            'partner_id': self.tenancy_id and self.tenancy_id.tenant_id and
            self.tenancy_id.tenant_id.id or False,
            'type': 'out_invoice',
            'vehicle_id': self.tenancy_id.vehicle_id.id or False,
            'date_invoice': datetime.now().strftime(
                DEFAULT_SERVER_DATE_FORMAT) or False,
            'journal_id': journal_ids and journal_ids[0].id or False,
            'account_id': self.tenancy_id and
            self.tenancy_id.tenant_id.property_account_receivable_id.id
            or False
        }
        if self.tenancy_id.main_cost:
            inv_values.update({'invoice_line_ids': [(0, 0, inv_line_values),
                                                    (0, 0, inv_line_main)]})
        else:
            inv_values.update(
                {'invoice_line_ids': [(0, 0, inv_line_values)]})
        acc_id = self.env['account.invoice'].create(inv_values)
        self.write({'invc_id': acc_id.id, 'inv': True})
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_form')[1]

        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    @api.multi
    def open_invoice(self):
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    @api.multi
    def create_move(self):
        """
        This button Method is used to create account move.
        @param self: The object pointer
        """
        move_line_obj = self.env['account.move.line']
        created_move_ids = []
        journal_ids = self.env['account.journal'].search(
            [('type', '=', 'sale')])
        for line in self:
            depreciation_date = datetime.now()
            company_currency = line.tenancy_id.company_id.currency_id.id
            current_currency = line.tenancy_id.currency_id.id
            sign = -1
            move_vals = {
                'name': line.tenancy_id.ref or False,
                'date': depreciation_date,
                'schedule_date': line.start_date,
                'journal_id': journal_ids and journal_ids.ids[0],
                'asset_id': line.tenancy_id.property_id.id or False,
                'source': line.tenancy_id.name or False,
            }
            move_id = self.env['account.move'].create(move_vals)
            if not line.tenancy_id.property_id.income_acc_id.id:
                raise Warning(
                    _('Please Configure Income Account from Property.'))
            cond1 = company_currency is not current_currency
            cond2 = -sign * line.tenancy_id.rent
            move_line_obj.create({
                'name': line.tenancy_id.name,
                'ref': line.tenancy_id.ref,
                'move_id': move_id.id,
                'account_id':
                line.tenancy_id.property_id.income_acc_id.id or False,
                'debit': 0.0,
                'credit': line.tenancy_id.rent,
                'journal_id': journal_ids and journal_ids.ids[0],
                'partner_id': line.tenancy_id.tenant_id.id or False,
                'currency_id': company_currency != current_currency and
                current_currency or False,
                'amount_currency': cond1 and cond2 or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create({
                'name': line.tenancy_id.name,
                'ref': 'Tenancy Rent',
                'move_id': move_id.id,
                'account_id':
                line.tenancy_id.tenant_id.property_account_receivable_id.id,
                'credit': 0.0,
                'debit': line.tenancy_id.rent,
                'journal_id': journal_ids and journal_ids.ids[0],
                'partner_id': line.tenancy_id.tenant_id.id or False,
                'currency_id': company_currency != current_currency and
                current_currency,
                'amount_currency': company_currency != current_currency and
                sign * line.tenancy_id.rent or 0.0,
                'analytic_account_id': line.tenancy_id.id,
                'date': depreciation_date,
                'asset_id': line.tenancy_id.property_id.id or False,
            })
            line.write({'move_id': move_id.id})
            created_move_ids.append(move_id.id)
            move_id.write({'ref': 'Tenancy Rent', 'state': 'posted'})
        return created_move_ids


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tenancy_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Rental Vehicle',
        help='Rental Vehicle Name.')

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        inv_obj = self.env['account.invoice']
        tenancy_invoice_rec = inv_obj.browse(self._context['active_ids'])
        tenancy_rent_obj = self.env['tenancy.rent.schedule']
        for invoice in tenancy_invoice_rec:
            rent_sched_ids = tenancy_rent_obj.search(
                [('invc_id', '=', invoice.id)])
            for rent_sched_rec in rent_sched_ids:
                if rent_sched_rec.invc_id:
                    amt = rent_sched_rec.invc_id.residual or 0.0
                rent_sched_rec.write({'pen_amt': amt})
                if rent_sched_rec.invc_id.state == 'paid':
                    rent_sched_rec.paid = True
                    rent_sched_rec.move_check = True
            if self._context.get('return', False) and \
                    self._context.get('active_model', False) and \
                    self._context['active_model'] == 'account.invoice':
                for invoice in self.env[self._context['active_model']].browse(
                            self._context.get('active_id', False)):
                    if invoice.new_tenancy_id:
                        invoice.new_tenancy_id.write({
                            'deposit_return': True,
                            'amount_return': invoice.amount_total})
        return res


class SaleCost(models.Model):
    _name = "sale.cost"
    _description = 'Sale Cost'
    _order = 'date'

    @api.one
    @api.depends('move_id')
    def _get_move_check(self):
        self.move_check = bool(self.move_id)

    date = fields.Date(
        string='Date')
    amount = fields.Float(
        string='Amount')
    name = fields.Char(
        string='Description',
        size=100)
    payment_details = fields.Char(
        string='Payment Details',
        size=100)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Purchase Entry')
    sale_property_id = fields.Many2one(
        comodel_name='account.asset.asset',
        string='Property')
    remaining_amount = fields.Float(
        string='Remaining Amount',
        help='Shows remaining amount in currency')
    move_check = fields.Boolean(
        string='Posted',
        compute='_get_move_check',
        method=True,
        store=True)
    rmn_amnt_per = fields.Float(
        string='Remaining Amount In %',
        help='Shows remaining amount in Percentage')
    invc_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')

    @api.multi
    def create_invoice(self):
        """
        This button Method is used to create account invoice.
        @param self: The object pointer
        """
        if not self.sale_property_id.customer_id:
            raise Warning(_('Please Select Customer'))
        if not self.sale_property_id.income_acc_id:
            raise Warning(_('Please Configure Income Account from Property.'))
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'sale')])

        inv_line_values = {
            'origin': 'Sale.Cost',
            'name': 'Purchase Cost For'+''+self.sale_property_id.name,
            'price_unit': self.amount or 0.00,
            'quantity': 1,
            'account_id': self.sale_property_id.income_acc_id.id,
        }

        inv_values = {
            'payment_term_id': self.sale_property_id.payment_term.id or False,
            'partner_id': self.sale_property_id.customer_id.id or False,
            'type': 'out_invoice',
            'property_id': self.sale_property_id.id or False,
            'invoice_line_ids': [(0, 0, inv_line_values)],
            'date_invoice': datetime.now().strftime(
                DEFAULT_SERVER_DATE_FORMAT) or False,
            'journal_id': account_jrnl_obj.id or False,
        }
        acc_id = self.env['account.invoice'].create(inv_values)
        self.write({'invc_id': acc_id.id, 'move_check': True})
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    @api.multi
    def open_invoice(self):
        """
        This Method is used to Open invoice
        @param self: The object pointer
        """
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'invoice_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }
