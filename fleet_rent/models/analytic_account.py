# See LICENSE file for full copyright and licensing details.
"""Analytic Account."""


import time
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT


class AccountAnalyticAccount(models.Model):
    """Account analytic account."""

    _inherit = "account.analytic.account"
    _order = 'ref'

    @api.multi
    @api.depends('account_move_line_ids')
    def _total_deb_cre_amt_calc(self):
        """
        Method is used to calculate Total income amount.

        @param self: The object pointer.
        """
        total = 0.0
        for tenancy_brw in self:
            total = tenancy_brw.total_debit_amt - tenancy_brw.total_credit_amt
            tenancy_brw.total_deb_cre_amt = total

    @api.multi
    @api.depends('account_move_line_ids')
    def _total_credit_amt_calc(self):
        """
        Method is used to calculate Total credit amount.

        @param self: The object pointer.
        """
        total = 0.0
        for tenancy_brw in self:
            if tenancy_brw.account_move_line_ids and \
                    tenancy_brw.account_move_line_ids.ids:
                for debit_amt in tenancy_brw.account_move_line_ids:
                    total += debit_amt.credit
            tenancy_brw.total_credit_amt = total

    @api.multi
    @api.depends('account_move_line_ids')
    def _total_debit_amt_calc(self):
        """
        Method is used to calculate Total debit amount.

        @param self: The object pointer.
        """
        total = 0.0
        for tenancy_brw in self:
            if tenancy_brw.account_move_line_ids and \
                    tenancy_brw.account_move_line_ids.ids:
                for debit_amt in tenancy_brw.account_move_line_ids:
                    total += debit_amt.debit
            tenancy_brw.total_debit_amt = total

    @api.one
    @api.depends('rent_schedule_ids', 'rent_schedule_ids.amount')
    def _total_amount_rent(self):
        """
        Method is used to calculate Total Rent of current Tenancy.

        @param self: The object pointer.

        @return: Calculated Total Rent.
        """
        tot = 0.00
        if self.rent_schedule_ids and self.rent_schedule_ids.ids:
            for propety_brw in self.rent_schedule_ids:
                tot += propety_brw.amount
        self.total_rent = tot

    @api.multi
    @api.depends('deposit')
    def _get_deposit(self):
        """
        Method is used to set deposit return and deposit received.

        boolean field accordingly to current Tenancy.

        @param self: The object pointer.
        """
        for tennancy in self:
            payment_ids = self.env['account.payment'].search(
                [('tenancy_id', '=', tennancy.id), ('state', '=', 'posted')])
            if payment_ids and payment_ids.ids:
                for payment in payment_ids:
                    tennancy.deposit_received = True

    @api.multi
    @api.depends('cost_id')
    def _total_cost_maint(self):
        """
        Method is used to calculate total maintenance.

        boolean field accordingly to current Tenancy.

        @param self: The object pointer.
        """
        for data in self:
            total = 0
            for data_1 in data.cost_id:
                total += data_1.cost
            data.main_cost = total

    @api.model
    def rent_send_mail(self):
        """Method to send mail."""
        model_obj = self.env['ir.model.data']
        send_obj = self.env['mail.template']
        rent_obj = self.env['account.analytic.account']
        res = model_obj.get_object_reference('fleet_rent',
                                             'email_template_edi_rent')
        server_obj = self.env['ir.mail_server']
        record_obj = model_obj.get_object_reference('fleet_rent',
                                                    'ir_mail_server_service')
        rec_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        vehicle_ids = rent_obj.search([('date', '=', rec_date)])
        temp_rec = False
        email_from_brw = ''
        if record_obj:
            email_from_brw = server_obj.browse(record_obj[1])
        if res:
            temp_rec = send_obj.browse(res[1])
        for rec in vehicle_ids:
            email_from = email_from_brw.smtp_user
            if not email_from:
                raise Warning(_("Warning"), _("May be Out Going Mail \
                                    server is not configuration."))
            if vehicle_ids and temp_rec:
                temp_rec.send_mail(rec.id, force_send=True)
        return True

    @api.one
    @api.depends('prop_id', 'multi_prop')
    def _total_prop_rent(self):
        tot = 0.00
        if self._context.get('is_tenancy_rent'):
            prop_val = self.prop_ids.ground_rent or 0.0
        else:
            prop_val = self.property_id.ground_rent or 0.0
        for pro_record in self:
            if self.multi_prop:
                for prope_ids in pro_record.prop_id:
                    tot += prope_ids.ground
                pro_record.rent = tot + prop_val
            else:
                pro_record.rent = prop_val

    def _get_odometer(self):
        fleetvehicalodometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleetvehicalodometer.search([
                ('vehicle_id', '=', record.vehicle_id.id)], limit=1,
                order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        fleetvehicalodometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleetvehicalodometer.search(
                [('vehicle_id', '=', record.vehicle_id.id)],
                limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise Warning(('User Error!\nYou can\'t enter odometer less \
                than previous odometer %s !') % (vehicle_odometer.value))
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date,
                        'vehicle_id': record.vehicle_id.id}
                fleetvehicalodometer.create(data)

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        """Method Onchange."""
        for rec in self:
            fleetvehicalodometer = self.env['fleet.vehicle.odometer']
            vehicle_odometer = fleetvehicalodometer.search([
                ('vehicle_id', '=', rec .vehicle_id.id)], limit=1,
                order='value desc')
            if rec.vehicle_id:
                rec.odometer = vehicle_odometer.value
#                 rec.odometer_unit = vehicle_odometer.unit

    @api.multi
    def change_color(self):
        """Method to change color."""
        for color in self:
            if color.state == 'new':
                color.color = 0
            elif color.state == 'open':
                color.color = 2
            elif color.state == 'pending':
                color.color = 1
            elif color.state == 'close':
                color.color = 5
            elif color.state == 'cancelled':
                color.color = 4

    vehicle_image = fields.Binary(related="vehicle_id.image",
                                  string="Vehicle Image", store=True)
    color = fields.Integer(string='Color', compute='change_color')
    odometer = fields.Float(
        compute='_get_odometer',
        inverse='_set_odometer',
        string='Last Odometer',
        help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(
        related='vehicle_id.odometer_unit',
        help='Unit of the odometer ', store=True)
    cancel_by_id = fields.Many2one('res.users', string="Rent Close By")
    date_cancel = fields.Datetime(string="Rent Close Date")
    contract_attachment = fields.Binary(
        string='Rental Vehicle Contract',
        help='Contract document attachment for selected vehicle')
    is_property = fields.Boolean(
        string='Is Property?')
    rent_entry_chck = fields.Boolean(
        string='Rent Entries Check',
        default=False)
    deposit_received = fields.Boolean(
        string='Deposit Received?',
        default=False,
        copy=False,
        multi='deposit',
        compute='_get_deposit',
        help="True if deposit amount received for current Rental Vehicle.")
    deposit_return = fields.Boolean(
        string='Deposit Returned?',
        default=False,
        copy=False,
        multi='deposit',
        type='boolean',
        compute='amount_return_compute',
        help="True if deposit amount returned for current Rental Vehicle.")
    ref = fields.Char(
        string='Reference',
        default="/")
    doc_name = fields.Char(
        string='Filename')
    date = fields.Datetime(
        compute="_create_date",
        string='Expiration Date',
        store=True,
        help="Rental Vehicle contract end date.")
    date_start = fields.Datetime(
        string='Start Date',
        default=lambda *a: time.strftime(DT),
        help="Rental Vehicle contract start date .")
    ten_date = fields.Datetime(
        string='Date',
        default=lambda *a: time.strftime(DT),
        help="Rental Vehicle contract creation date.")
    amount_fee_paid = fields.Integer(
        string='Amount of Fee Paid')
    manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Account Manager',
        help="Manager of Rental Vehicle.")
    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        help="Name of Vehicle.")
    vehicle_property_id = fields.Many2one(
        comodel_name='account.asset.asset',
        string='Vehicle Name',
        help="Name of Vehicle.")
    tenant_id = fields.Many2one(
        comodel_name='res.partner',
        string='Tenant',
        help="Tenant Name of Rental Vehicle.")
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        help="Contact person name.")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        help="The optional other currency if it is a multi-currency entry.")
    cr_rent_btn = fields.Boolean('Hide Rent Button')
    rent_schedule_ids = fields.One2many(
        comodel_name='tenancy.rent.schedule',
        inverse_name='tenancy_id',
        string='Rent Schedule')
    account_move_line_ids = fields.One2many(
        comodel_name='account.move.line',
        inverse_name='analytic_account_id',
        string='Entries',
        readonly=True,
        states={'draft': [('readonly', False)]})
    rent = fields.Float(
        string='Rental Vehicle Rent',
        default=0.0,
        currency_field='currency_id',
        help="Rental vehicle rent for selected vehicle per rent type.")
    deposit = fields.Float(
        string='Deposit',
        default=0.0,
        copy=False,
        currency_field='currency_id',
        help="Deposit amount for Rental Vehicle.")
    total_rent = fields.Float(
        string='Total Rent',
        store=True,
        readonly=True,
        currency_field='currency_id',
        compute='_total_amount_rent',
        help='Total rent of this Rental Vehicle.')
    amount_return = fields.Float(
        string='Deposit Returned',
        default=0.0,
        copy=False,
        currency_field='currency_id',
        help="Deposit Returned amount for Rental Vehicle.")
    total_debit_amt = fields.Float(
        string='Total Debit Amount',
        default=0.0,
        compute='_total_debit_amt_calc',
        currency_field='currency_id')
    total_credit_amt = fields.Float(
        string='Total Credit Amount',
        default=0.0,
        compute='_total_credit_amt_calc',
        currency_field='currency_id')
    total_deb_cre_amt = fields.Float(
        string='Total Expenditure',
        default=0.0,
        compute='_total_deb_cre_amt_calc',
        currency_field='currency_id')
    description = fields.Text(
        string='Description',
        help='Additional Terms and Conditions')
    duration_cover = fields.Text(
        string='Duration of Cover',
        help='Additional Notes')
    acc_pay_dep_rec_id = fields.Many2one(
        comodel_name='account.voucher',
        string='Rental Account Manager',
        help="Manager of Rental Vehicle.")
    acc_pay_dep_ret_id = fields.Many2one(
        comodel_name='account.voucher',
        string='Account Manager',
        help="Manager of Rental Vehicle.")
    rent_type_id = fields.Many2one(
        comodel_name='rent.type',
        string='Rent Type')
    deposit_scheme_type = fields.Selection(
        [('insurance', 'Insurance-based')],
        'Type of Scheme')
    state = fields.Selection(
        [('draft', 'New'),
         ('open', 'In Progress'), ('pending', 'To Renew'),
         ('close', 'Closed'), ('cancelled', 'Cancelled')],
        string='Status',
        required=True,
        copy=False,
        default='draft')
    main_cost = fields.Float(
        string='Maintenance Cost',
        default=0.0,
        store=True,
        compute='_total_cost_maint',
        help="insert maintenance cost")
    cost_id = fields.One2many(
        comodel_name='maintenance.cost',
        inverse_name='tenancy',
        string='cost')
    invc_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')
    multi_prop = fields.Boolean(
        string='Multiple Property',
        help="Check this box Multiple property.")

    @api.model
    def rent_done_cron(self):
        """Method to rent done cron."""
        acc_obj = self.env['account.analytic.account']
        rent_obj = self.env['tenancy.rent.schedule']
        for rec in acc_obj.search([('date', '!=', False),
                                   ('state', '!=', 'close')]):
            records = []
            if rec.rent_schedule_ids:
                records = rent_obj.search([('paid', '=', False),
                                           ('id', 'in',
                                            rec.rent_schedule_ids.ids)])
            if not records:
                if datetime.now() >= datetime.strptime(str(rec.date), DT):
                    reason = "This Rent Order is auto completed due to your \
                                rent limit is over."
                    rec.write({'state': 'close',
                               'duration_cover': reason,
                               'date_cancel': datetime.now(),
                               'cancel_by_id': self._uid})
        return True

    @api.constrains('date_start', 'date')
    def check_date_overlap(self):
        """
        Method used to check the from date smaller than.

        the Expiration date.

        @param self : object pointer
        """
        for ver in self:
            if ver.date_start and ver.date:
                dt_from = ver.date_start.strftime(DT)
                dt_to = ver.date.strftime(DT)
                if dt_to < dt_from:
                    raise ValidationError(
                        'Expiration Date Should Be Greater Than Start Date!')

    @api.model
    def default_get(self, fields):
        """
        Method is return if vehicle state is write-off then its.

        returns false and if vehicle state is other then its returns true.
        """
        res = super(AccountAnalyticAccount, self).default_get(fields)
        cr, uid, context = self.env.args
        context = dict(context)
        fleet_obj = self.env['fleet.vehicle']
        if self._context.get('active_id'):
            vehicle_id = fleet_obj.browse(context['active_id'])
            if vehicle_id.state == 'write-off':
                res['vehicle_id'] = False
            if vehicle_id.state == 'in_progress':
                res['vehicle_id'] = False
        return res

    @api.model
    def create(self, vals):
        """
        Method is used to overrides orm create method.

        To change state and tenant of related property.

        @param self: The object pointer.

        @param vals: dictionary of fields value.
        """
        vehicle_id = vals.get('vehicle_id', False)
        st_dt = vals.get('date_start', False)
        vehicle_obj = self.env['fleet.vehicle']
        veh_ser_obj = self.env['fleet.vehicle.log.services']
        vehicle_rec = vehicle_obj.browse(vehicle_id)
        veh_ser_rec = veh_ser_obj.search([('vehicle_id', '=', vehicle_id),
                                          ('date_complete', '>', st_dt)])
        if vehicle_rec.state == 'in_progress' and veh_ser_rec:
            raise ValidationError('This Vehicle In Service. So You Can Not\
                                        Create Rent Order For This Vehicle.')
        if not vals:
            vals = {}
        if 'tenant_id' in vals:
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'account.analytic.account')
            vals.update({'is_property': True})
        res = super(AccountAnalyticAccount, self).create(vals)
        st_dt = res.date_start
        en_dt = res.date
        veh_id = res.vehicle_id and res.vehicle_id.id or False
        anlytic_obj = self.env['account.analytic.account']
        avilable_records = anlytic_obj.search([('state', '!=', 'close'),
                                               ('vehicle_id', '=', veh_id),
                                               ('id', '!=', res.id)])
        if avilable_records:
            for rec in avilable_records:
                if rec.date_start and rec.date:
                    cond1 = (st_dt < rec.date_start < en_dt)
                    cond2 = (st_dt < rec.date < en_dt)
                    if cond1 or cond2:
                        raise ValidationError('This vehicle rent is \
                            already available. You can not create another \
                            rent for this vehicle on same rent date.')
        return res

    @api.multi
    def write(self, vals):
        """
        Method is used to overrides orm write method.

        to change state and tenant of related property.

        @param self: The object pointer.

        @param vals: dictionary of fields value.
        """
        vehicle_id = self.vehicle_id.id
        st_dt = vals.get('date_start', False)
        vehicle_obj = self.env['fleet.vehicle']
        veh_ser_obj = self.env['fleet.vehicle.log.services']
        vehicle_rec = vehicle_obj.browse(vehicle_id)
        veh_ser_rec = veh_ser_obj.search([('vehicle_id', '=', vehicle_id),
                                          ('date_complete', '>', st_dt)])
        if vehicle_rec.state == 'in_progress' and veh_ser_rec:
            raise ValidationError('This Vehicle In Service. So You Can Not\
                                        Create Rent Order For This Vehicle.')
        rec = super(AccountAnalyticAccount, self).write(vals)

        for rent_rec in self:
            if vals.get('state'):
                if vals['state'] == 'open':
                    rent_rec.vehicle_id.write({
                        'state': 'rent'})
                if vals['state'] == 'close':
                    rent_rec.vehicle_id.write(
                        {'state': 'complete'})

            st_dt = str(rent_rec.date_start)
            en_dt = str(rent_rec.date)
            veh_id = rent_rec.vehicle_id and rent_rec.vehicle_id.id or False
            anlytic_obj = self.env['account.analytic.account']
            avilable_records = anlytic_obj.search([('state', '!=', 'close'),
                                                   ('vehicle_id', '=', veh_id),
                                                   ('id', '!=', rent_rec.id)])
            if avilable_records:
                for record in avilable_records:
                    if record.date_start and record.date and record.vehicle_id:
                        cond1 = (st_dt < str(record.date_start) < en_dt)
                        cond2 = (st_dt < str(record.date) < en_dt)
                        if cond1 or cond2:
                            raise ValidationError('This vehicle rent is \
                                already available. You can not create another \
                                rent for this vehicle on same rent date.')
        return rec

    @api.multi
    def unlink(self):
        """
        Override orm unlink method.

        @param self: The object pointer.

        @return: True/False.
        """
        rent_ids = []
        for tenancy_rec in self:
            if tenancy_rec.state == 'open':
                raise Warning(
                    _('The Rent Is In-Progress So You Can Not Delete It.'))
            analytic_ids = self.env['account.analytic.line'].search(
                [('account_id', '=', tenancy_rec.id)])
            if analytic_ids and analytic_ids.ids:
                analytic_ids.unlink()
            rent_ids = self.env['tenancy.rent.schedule'].search(
                [('tenancy_id', '=', tenancy_rec.id)])
            post_rent = [x.id for x in rent_ids if x.move_check is True]
            if post_rent:
                raise Warning(
                    _('You cannot delete Tenancy record, if any related Rent \
                    Schedule entries are in posted.'))
            else:
                rent_ids.unlink()
            if tenancy_rec.vehicle_id.driver_id and \
                    tenancy_rec.vehicle_id.driver_id.id:
                releted_user = tenancy_rec.vehicle_id.driver_id.id
                new_ids = self.env['res.users'].search(
                    [('partner_id', '=', releted_user)])
                if releted_user and new_ids and new_ids.ids:
                    new_ids.write(
                        {'tenant_ids': [(3, tenancy_rec.tenant_id.id)]})
            tenancy_rec.vehicle_id.write(
                {'state': 'inspection', 'current_tenant_id': False})
        return super(AccountAnalyticAccount, self).unlink()

    @api.depends('amount_return')
    def amount_return_compute(self):
        """
        When you change Deposit field value, this method will change.

        amount_fee_paid field value accordingly.

        @param self: The object pointer.
        """
        for rec in self:
            if rec.amount_return > 0.00:
                rec.deposit_return = True

    @api.multi
    def button_receive(self):
        """
        Button method is used to open the related.

        Account payment form view.

        @param self: The object pointer.

        @return: Dictionary of values.
        """
        if not self._ids:
            return []
        for tenancy_rec in self:
            jonral_type = \
                self.env['account.journal'].search([('type', '=', 'cash')])
            if tenancy_rec.acc_pay_dep_rec_id and \
                    tenancy_rec.acc_pay_dep_rec_id.id:
                acc_pay_form_id = \
                    self.env['ir.model.data'].get_object_reference(
                        'account', 'view_account_payment_form')[1]
                return {
                    'view_type': 'form',
                    'view_id': acc_pay_form_id,
                    'view_mode': 'form',
                    'res_model': 'account.payment',
                    'res_id': self.acc_pay_dep_rec_id.id,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': {
                        'default_partner_id': tenancy_rec.tenant_id.id,
                        'default_partner_type': 'customer',
                        'default_journal_id': jonral_type and
                        jonral_type.ids[0] or False,
                        'default_payment_type': 'inbound',
                        'default_type': 'receipt',
                        'default_communication': 'Deposit Received',
                        'default_tenancy_id': tenancy_rec.id,
                        'default_amount': tenancy_rec.deposit,
                        'default_property_id':
                        tenancy_rec.vehicle_id.id,
                        'close_after_process': True,
                    }
                }
            if tenancy_rec.deposit == 0.00:
                raise Warning(_('Please Enter Deposit amount.'))
            if tenancy_rec.deposit < 0.00:
                raise Warning(
                    _('The deposit amount must be strictly positive.'))
            ir_id = self.env['ir.model.data']._get_id(
                'account', 'view_account_payment_form')
            ir_rec = self.env['ir.model.data'].browse(ir_id)
            return {
                'view_mode': 'form',
                'view_id': [ir_rec.res_id],
                'view_type': 'form',
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': {
                    'default_partner_id': tenancy_rec.tenant_id.id,
                    'default_partner_type': 'customer',
                    'default_journal_id': jonral_type and
                    jonral_type.ids[0] or False,
                    'default_payment_type': 'inbound',
                    'default_type': 'receipt',
                    'default_communication': 'Deposit Received',
                    'default_tenancy_id': tenancy_rec.id,
                    'default_amount': tenancy_rec.deposit,
                    'default_property_id': tenancy_rec.vehicle_id.id,
                    'close_after_process': True,
                }
            }

    @api.multi
    def button_return(self):
        """Method button return."""
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'purchase')])
        if not self.vehicle_id.expence_acc_id.id:
            raise Warning(_('Please Configure Expense Account from Vehicle'))

        inv_line_values = {
            'name': 'Deposit Return' or "",
            'origin': 'account.analytic.account' or "",
            'quantity': 1,
            'account_id': self.vehicle_id.expence_acc_id.id or False,
            'price_unit': self.deposit or 0.00,
            'account_analytic_id': self.id or False,
        }
        if self.multi_prop:
            for data in self.prop_id:
                for account in data.property_ids.income_acc_id:
                    account_id = account.id
                inv_line_values.update({'account_id': account_id})

        inv_values = {
            'origin': 'Deposit Return For ' + self.name or "",
            'type': 'in_invoice',
            'property_id': self.vehicle_id.id,
            'partner_id': self.tenant_id.id or False,
            'account_id':
            self.tenant_id.property_account_payable_id.id or False,
            'invoice_line': [(0, 0, inv_line_values)],
            'date_invoice': datetime.now().strftime(DT) or False,
            'new_tenancy_id': self.id,
            'reference': self.ref,
            'journal_id': account_jrnl_obj and
            account_jrnl_obj.ids[0] or False,
        }

        acc_id = self.env['account.invoice'].create(inv_values)
        self.write({'invc_id': acc_id.id})
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
            'context': self._context,
        }

    @api.multi
    def button_start(self):
        """
        Button method is used to Change Tenancy state to Open.

        @param self: The object pointer.
        """
        if self.rent <= 1:
            raise ValidationError("You Can't Enter Rental Vehicle Rent \
                                    Less Than One(1).")
        return self.write({'state': 'open', 'rent_entry_chck': False})

    @api.multi
    def button_close(self):
        """
        Button method is used to Change Tenancy state to close.

        @param self: The object pointer.
        """
        return {
            'name': ('Rent Close Form'),
            'res_model': 'rent.close.reason',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'
        }

    @api.multi
    def button_set_to_draft(self):
        """
        Button method is used to Change Tenancy state to close.

        @param self: The object pointer.
        """
        for rec in self:
            if rec.state == 'open':
                if rec.rent_schedule_ids:
                    raise Warning(
                        _('You can not set draft stage Because \
                        rent schedule is created.'))
            rec.state = 'draft'

    @api.multi
    def button_set_to_renew(self):
        """
        Method is used to open Tenancy renew wizard.

        @param self: The object pointer.

        @return: Dictionary of values.
        """
        cr, uid, context = self.env.args
        context = dict(context)
        if context is None:
            context = {}
        for tenancy_brw in self:
            tenancy_brw.cr_rent_btn = False
            if tenancy_brw.vehicle_id.state == 'write-off':
                raise Warning(_('You can not renew rent for %s \
                                because this vehicle is in \
                                write-off.') % (tenancy_brw.vehicle_id.name))
            tenancy_rent_ids = self.env['tenancy.rent.schedule'].search(
                [('tenancy_id', '=', tenancy_brw.id),
                 ('move_check', '=', False)])
            if len(tenancy_rent_ids.ids) > 0:
                raise Warning(
                    _('In order to Renew a Tenancy, Please make all related \
                    Rent Schedule entries posted.'))
            date = datetime.strptime(str(
                tenancy_brw.date), "%Y-%m-%d %H:%M:%S") + \
                timedelta(days=1)
            date1 = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
            context.update({'edate': date1})
            return {
                'name': ('Tenancy Renew Wizard'),
                'res_model': 'renew.tenancy',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_start_date': context.get('edate')}
            }

    @api.model
    def cron_property_states_changed(self):
        """
        Method is called by Scheduler for change property state.

        according to tenancy state.

        @param self: The object pointer.
        """
        curr_date = datetime.now().date()
        tncy_ids = self.search([('date_start', '<=', curr_date),
                                ('date', '>=', curr_date),
                                ('state', '=', 'open'),
                                ('is_property', '=', True)])
        if len(tncy_ids.ids) != 0:
            for tncy_data in tncy_ids:
                if tncy_data.property_id and tncy_data.property_id.id:
                    tncy_data.property_id.write(
                        {'state': 'normal', 'color': 7})
        return True

    @api.model
    def cron_property_tenancy(self):
        """
        Method is called by Scheduler to send email.

        to tenant as a reminder for rent payment.

        @param self: The object pointer.
        """
        tenancy_ids = []
        due_date = datetime.now().date() + relativedelta(days=7)
        tncy_ids = self.search(
            [('is_property', '=', True), ('state', '=', 'open')])
        for tncy_data in tncy_ids:
            tncy_rent_ids = self.env['tenancy.rent.schedule'].search(
                [('tenancy_id', '=', tncy_data.id),
                 ('start_date', '=', due_date)])
            if tncy_rent_ids and tncy_rent_ids.ids:
                tenancy_ids.append(tncy_data.id)
        tenancy_sort_ids = list(set(tenancy_ids))
        model_data_id = self.env['ir.model.data'].get_object_reference(
            'property_management', 'property_email_template')[1]
        template_brw = self.env['mail.template'].browse(model_data_id)
        for tenancy in tenancy_sort_ids:
            template_brw.send_mail(
                tenancy, force_send=True, raise_exception=False)
        return True

    @api.multi
    @api.depends('rent_type_id', 'date_start')
    def _create_date(self):
        for rec in self:
            if rec.rent_type_id and rec.date_start:
                if rec.rent_type_id.renttype == 'Months':
                    rec.date = \
                        datetime.strptime(str(rec.date_start), DT) + \
                        relativedelta(months=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Years':
                    rec.date = datetime.strptime(str(rec.date_start), DT) + \
                        relativedelta(years=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Weeks':
                    rec.date = datetime.strptime(str(rec.date_start), DT) + \
                        relativedelta(weeks=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Days':
                    rec.date = datetime.strptime(str(rec.date_start), DT) + \
                        relativedelta(days=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Hours':
                    rec.date = datetime.strptime(str(rec.date_start), DT) + \
                        relativedelta(hours=int(rec.rent_type_id.duration))
        return True

    @api.multi
    def create_rent_schedule(self):
        """
        Button method is used to create rent schedule Lines.

        @param self: The object pointer.
        """
        for tenancy_rec in self:
            for rent_line in tenancy_rec.rent_schedule_ids:
                if rent_line.paid is False and rent_line.move_check is False:
                    raise Warning(
                        _('You can\'t create new rent schedule Please make \
                        all related Rent Schedule entries paid.'))
            rent_obj = self.env['tenancy.rent.schedule']
            if tenancy_rec.date_start and tenancy_rec.rent_type_id and \
                    tenancy_rec.rent_type_id.renttype:
                interval = int(tenancy_rec.rent_type_id.duration)
                d1 = datetime.strptime(str(tenancy_rec.date_start), DT)
                if tenancy_rec.rent_type_id.renttype == 'Months':
                    for i in range(0, interval):
                        d1 = d1 + relativedelta(months=int(1))
                        rent_obj.create({
                            'start_date': d1.strftime(DT),
                            'amount': tenancy_rec.rent,
                            'vehicle_id': tenancy_rec.vehicle_id and
                            tenancy_rec.vehicle_id.id or False,
                            'tenancy_id': tenancy_rec.id,
                            'currency_id': tenancy_rec.currency_id.id or False,
                            'rel_tenant_id': tenancy_rec.tenant_id.id or False
                        })
                if tenancy_rec.rent_type_id.renttype == 'Years':
                    for i in range(0, interval):
                        d1 = d1 + relativedelta(years=int(1))
                        rent_obj.create({
                            'start_date': d1.strftime(DT),
                            'amount': tenancy_rec.rent,
                            'vehicle_id': tenancy_rec.vehicle_id and
                            tenancy_rec.vehicle_id.id or False,
                            'tenancy_id': tenancy_rec.id,
                            'currency_id': tenancy_rec.currency_id.id or False,
                            'rel_tenant_id': tenancy_rec.tenant_id.id or False
                        })
                if tenancy_rec.rent_type_id.renttype == 'Weeks':
                    for i in range(0, interval):
                        d1 = d1 + relativedelta(weeks=int(1))
                        rent_obj.create({
                            'start_date': d1.strftime(DT),
                            'amount': tenancy_rec.rent,
                            'vehicle_id': tenancy_rec.vehicle_id and
                            tenancy_rec.vehicle_id.id or False,
                            'tenancy_id': tenancy_rec.id,
                            'currency_id': tenancy_rec.currency_id.id or False,
                            'rel_tenant_id': tenancy_rec.tenant_id.id or False
                        })
                if tenancy_rec.rent_type_id.renttype == 'Days':
                    rent_obj.create({
                        'start_date': d1.strftime(DT),
                        'amount': tenancy_rec.rent * interval,
                        'vehicle_id': tenancy_rec.vehicle_id and
                        tenancy_rec.vehicle_id.id or False,
                        'tenancy_id': tenancy_rec.id,
                        'currency_id': tenancy_rec.currency_id.id or False,
                        'rel_tenant_id': tenancy_rec.tenant_id.id or False
                    })
                if tenancy_rec.rent_type_id.renttype == 'Hours':
                    rent_obj.create({
                        'start_date': d1.strftime(DT),
                        'amount': tenancy_rec.rent * interval,
                        'vehicle_id': tenancy_rec.vehicle_id and
                        tenancy_rec.vehicle_id.id or False,
                        'tenancy_id': tenancy_rec.id,
                        'currency_id': tenancy_rec.currency_id.id or False,
                        'rel_tenant_id': tenancy_rec.tenant_id.id or False
                    })
                tenancy_rec.cr_rent_btn = True
        return True
