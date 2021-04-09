# See LICENSE file for full copyright and licensing details.
"""Fleet Rent Model."""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import ustr,date_utils, DEFAULT_SERVER_DATE_FORMAT as DF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTF


class FleetRent(models.Model):
    """Fleet Rent Model."""

    _name = "fleet.rent"
    _inherit = ['mail.thread']
    _description = "Fleet Rent"

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Method to display owner name."""
        for rent in self:
            if rent.vehicle_id:
                # we added sudo in below code to fix the access issue with rent user
                rent.vehicle_owner = rent.vehicle_id.sudo().vehicle_owner.name

    @api.onchange('vehicle_id')
    def change_odometer(self):
        """Method to display odometer value."""
        for rent in self:
            if rent.vehicle_id:
                rent.odometer = rent.vehicle_id.odometer

    @api.depends('account_move_line_ids')
    def _compute_total_deb_cre_amt_calc(self):
        """Method to calculate Total income amount."""
        for rent in self:
            rent.total_deb_cre_amt = \
                rent.total_debit_amt - rent.total_credit_amt

    def _compute_total_credit_amt_calc(self):
        """Method to calculate Total credit amount."""
        for rent in self:
            rent.total_credit_amt = sum(acc_mov_line.credit
                                        for acc_mov_line in
                                        rent.account_move_line_ids) or 0.0

    # @api.depends('account_move_line_ids', 'account_move_line_ids.debit')
    def _compute_total_debit_amt_calc(self):
        """Method to calculate Total debit amount."""
        for rent in self:
            rent.total_debit_amt = sum(acc_mov_line.debit
                                       for acc_mov_line in
                                       rent.account_move_line_ids) or 0.0

    @api.model
    def default_get(self, fields):
        """Overridden method to update odometer in fleet rent."""
        context = (self._context or {})
        vehical_obj = self.env['fleet.vehicle']
        res = super(FleetRent, self).default_get(fields)
        if res.get('vehicle_id', False):
            vehicle = vehical_obj.browse(res['vehicle_id'])
            if context.get('from_rent_smartbutton', False) and \
                    vehicle.state == 'write-off':
                raise Warning("Rent can not create when vehicle "
                              "in write-off state !!")
            if vehicle.state == 'write-off':
                res.update({'vehicle_id': False,
                            'odometer': vehicle.odometer or 0.0})
            else:
                res.update({'odometer': vehicle.odometer or 0.0})
        return res

    def _compute_get_odometer(self):
        odometer_obj = self.env['fleet.vehicle.odometer']
        for rent in self:
            if rent.vehicle_id:
                odometer = odometer_obj.search([
                    ('vehicle_id', '=', rent.vehicle_id.id)], limit=1,
                    order='value desc')
                if odometer:
                    rent.odometer = odometer.value
                else:
                    rent.odometer = 0

    def _compute_set_odometer(self):
        odometer_obj = self.env['fleet.vehicle.odometer']
        for rent in self:
            if rent.vehicle_id:
                odometer = odometer_obj.search(
                    [('vehicle_id', '=', rent.vehicle_id.id)],
                    limit=1, order='value desc')
                if rent.odometer < odometer.value:
                    raise Warning(_('User Error!\nYou can\'t add odometer less '
                                    'than previous odometer value %s !') % odometer.value)
                if rent.odometer:
                    date = fields.Date.context_today(rent)
                    odometer_obj.create({
                        'value': rent.odometer,
                        'date': date,
                        'vehicle_id': rent.vehicle_id.id
                    })

    @api.depends('deposit_amt')
    def _compute_get_deposit(self):
        """Method to set deposit return and deposit received."""
        for rent in self:
            deposit_inv_ids = self.env['account.move'].search([
                ('fleet_rent_id', '=', rent.id), ('type', '=', 'out_invoice'),
                ('state', 'in', ['posted']),
                ('is_deposit_inv', '=', True)])
            residual_amt = 0.0
            rent.deposit_received = False
            if deposit_inv_ids:
                residual_amt = sum(
                    [dp_inv.amount_residual for dp_inv in deposit_inv_ids if dp_inv.amount_residual > 0.0])
                if residual_amt > 0.0:
                    rent.deposit_received = False
                else:
                    rent.deposit_received = True

    @api.depends('amount_return')
    def _compute_amount_return(self):
        """Method to set the deposit return value."""
        for rent in self:
            credit_inv_ids = self.env['account.move'].search([
                ('fleet_rent_id', '=', rent.id), ('type', '=', 'out_refund'),
                # ('state', 'in', ['open', 'in_payment', 'paid']),
                ('state', 'in', ['posted']),
                ('is_deposit_return_inv', '=', True)])
            residual_amt = 0.0
            rent.is_deposit_return = False
            if credit_inv_ids:
                residual_amt = sum(
                    [credit_inv.amount_residual for credit_inv in credit_inv_ids if credit_inv.amount_residual > 0.0])
                if residual_amt > 0.0:
                    rent.is_deposit_return = False
                else:
                    rent.is_deposit_return = True

    @api.depends('rent_type_id', 'date_start')
    def _compute_create_date(self):
        for rent in self:
            if rent.rent_type_id and rent.date_start:
                if rent.rent_type_id.renttype == 'Months':
                    rent.date_end = rent.date_start + \
                                    relativedelta(months=int(rent.rent_type_id.duration))
                if rent.rent_type_id.renttype == 'Years':
                    rent.date_end = rent.date_start + \
                                    relativedelta(years=int(rent.rent_type_id.duration))
                if rent.rent_type_id.renttype == 'Weeks':
                    rent.date_end = rent.date_start + \
                                    relativedelta(weeks=int(rent.rent_type_id.duration))
                if rent.rent_type_id.renttype == 'Days':
                    rent.date_end = rent.date_start + \
                                    relativedelta(days=int(rent.rent_type_id.duration))
                if rent.rent_type_id.renttype == 'Hours':
                    rent.date_end = rent.date_start + \
                                    relativedelta(hours=int(rent.rent_type_id.duration))

    @api.depends('maintanance_ids', 'maintanance_ids.cost')
    def _compute_total_maintenance_cost(self):
        """Method to calculate total maintenance."""
        for rent in self:
            rent.maintenance_cost = sum(cost_line.cost for cost_line in
                                        rent.maintanance_ids) or  0.0

    @api.depends('rent_schedule_ids', 'rent_schedule_ids.amount')
    def _compute_total_amount_rent(self):
        """Method to calculate Total Rent of current Tenancy."""
        for rent in self:
            rent.total_rent = sum(rent_line.amount for rent_line in
                                  rent.rent_schedule_ids) or 0.0

    name = fields.Char(string="Name", translate=True,
                       copy=False, default="New")
    state = fields.Selection([('draft', 'New'), ('open', 'In Progress'),
                              ('pending', 'To Renew'), ('close', 'Closed'),
                              ('done', 'Done'),
                              ('cancelled', 'Cancelled')],
                             string='Status', default='draft', copy=False)
    vehicle_id = fields.Many2one('fleet.vehicle',
                                 string='Vehicle',
                                 help="Name of Vehicle.")
    vehicle_owner = fields.Char(string="vehicle_owner")
    tenant_id = fields.Many2one('res.users',
                                string='Tenant',
                                help="Tenant Name of Rental Vehicle.")
    fleet_tenant_id = fields.Many2one(related="tenant_id.partner_id",
                                      store=True,
                                      string='Fleet Tenant',
                                      help="Tenant Name of Rental Vehicle.")
    manager_id = fields.Many2one('res.users',
                                 string='Account Manager',
                                 help="Manager of Rental Vehicle.")
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env[
                                      'res.company']._get_user_currency(),
                                  string='Currency',
                                  help="The optional other currency \
                                  if it is a multi-currency entry.")
    odometer = fields.Float(compute='_compute_get_odometer',
                            inverse='_compute_set_odometer',
                            string='Last Odometer',
                            help='Odometer measure of the vehicle at \
                            the moment of this log')
    odometer_unit = fields.Selection(related='vehicle_id.odometer_unit',
                                     help='Unit of the vehicle odometer.',
                                     store=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env[
                                     'res.company']._company_default_get(),
                                 help="Name of Company.")
    rent_amt = fields.Float(string='Rental Vehicle Rent',
                            currency_field='currency_id',
                            help="Rental vehicle rent for selected \
                                vehicle per rent type.",
                            copy=False)
    deposit_amt = fields.Float(string='Deposit Amount',
                               copy=False,
                               currency_field='currency_id',
                               help="Deposit amount for Rental Vehicle.")
    deposit_received = fields.Boolean(compute='_compute_get_deposit',
                                      string='Deposit Received?',
                                      copy=False,
                                      help="True if deposit amount received \
                                      for current Rental Vehicle.")
    contact_id = fields.Many2one('res.partner',
                                 string='Contact',
                                 help="Contact person name.")
    contract_dt = fields.Datetime(string='Contract Creation',
                                  default=lambda *a: datetime.now(),
                                  help="Rental Vehicle contract \
                                  creation date.")
    amount_return = fields.Float(string='Deposit Returned',
                                 copy=False,
                                 currency_field='currency_id',
                                 help="Deposit Returned amount for \
                                 Rental Vehicle.")
    is_deposit_return = fields.Boolean(compute='_compute_amount_return',
                                       string='Deposit Returned?',
                                       copy=False,
                                       help="True if deposit amount returned \
                                       for current Rental Vehicle.")
    maintenance_cost = fields.Float(compute='_compute_total_maintenance_cost',
                                    string='Maintenance Cost',
                                    store=True,
                                    help="Add Maintenance Cost.")
    date_start = fields.Datetime(string='Start Date',
                                 default=lambda *a: datetime.now(),
                                 help="Rental Vehicle contract start date.")
    date_end = fields.Datetime(compute="_compute_create_date",
                               string='Expiration Date',
                               store=True,
                               help="Rental Vehicle contract end date.")
    rent_type_id = fields.Many2one('rent.type',
                                   string='Rent Type')
    total_rent = fields.Float(compute='_compute_total_amount_rent',
                              string='Total Rent',
                              currency_field='currency_id',
                              store=True,
                              help='Total rent of this Rental Vehicle.')
    rent_close_by = fields.Many2one(
        'res.users', string="Rent Close By", copy=False)
    date_close = fields.Datetime(string="Rent Close Date", copy=False)

    rent_schedule_ids = fields.One2many('tenancy.rent.schedule',
                                        'fleet_rent_id',
                                        string='Rent Schedule')
    maintanance_ids = fields.One2many('maintenance.cost',
                                      'fleet_rent_id',
                                      string='Maintenance Costs')
    description = fields.Text(string="Description")
    account_move_line_ids = fields.One2many('account.move.line',
                                            'fleet_rent_id',
                                            string='Entries')
    account_payment_ids = fields.One2many(
        'account.payment', 'fleet_rent_id', string='Payment Entries')
    total_debit_amt = fields.Float(compute='_compute_total_debit_amt_calc',
                                   string='Total Debit Amount',
                                   currency_field='currency_id')
    total_credit_amt = fields.Float(compute='_compute_total_credit_amt_calc',
                                    string='Total Credit Amount',
                                    currency_field='currency_id')
    total_deb_cre_amt = fields.Float(compute='_compute_total_deb_cre_amt_calc',
                                     string='Total Expenditure',
                                     currency_field='currency_id')
    invoice_id = fields.Many2one('account.move',
                                 string='Invoice')
    cr_rent_btn = fields.Boolean(string='Hide Rent Button', copy=False)
    # acc_pay_dep_rec_id = fields.Many2one('account.voucher',
    #                                      string='Rental Account Manager',
    #                                      help="Manager of Rental Vehicle.")
    close_reson = fields.Text(string='Rent Close Reason',
                              help='Rent Close Reason.')
    # vehicle_property_id = fields.Many2one('account.asset.asset',
    #                                       string='Property')
    invoice_count = fields.Integer(compute='_compute_count_invoice',
                                   string="Deposit Receive")
    refund_inv_count = fields.Integer(compute='_compute_count_refund_invoice',
                                      string="Refund")

    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        for rec in self:
            duplicate_rent = self.env['fleet.rent'].search([
                ('state', '=', ['open', 'pending', 'close']),
                ('id', '!=', rec.id), ('vehicle_id', '=', rec.vehicle_id.id)])
            if duplicate_rent:
                raise ValidationError(_("Vehicle Rent Order is already "
                                        "available for this vehicle !! \n Choose other"
                                        " vehicle and Prepare new rent order !!"))

    def _compute_count_invoice(self):
        """Method to count Out Invoice."""
        obj = self.env['account.move']
        for rent in self:
            rent.invoice_count = obj.search_count([
                ('type', '=', 'out_invoice'),
                ('fleet_rent_id', '=', rent.id),
                ('is_deposit_inv', '=', True)])

    def _compute_count_refund_invoice(self):
        """Method to count Refund Invoice."""
        obj = self.env['account.move']
        for rent in self:
            rent.refund_inv_count = obj.search_count([
                ('type', '=', 'out_refund'),
                ('fleet_rent_id', '=', rent.id),
                ('is_deposit_return_inv', '=', True)])

    # @api.model
    # def rent_send_mail(self):
    #     """Method to send mail."""
    #     rent_obj = self.env['fleet.rent']
    #     mail_temp_rec = self.env.ref('fleet_rent.email_template_edi_rent')
    #     rent_ids = rent_obj.search([('date_end', '>=', date_utils.subtract(fields.Datetime.now(), days=5))])
    #     if rent_ids and mail_temp_rec:
    #         for rent in rent_ids:
    #             mail_temp_rec.send_mail(rent.id, force_send=True)

    # @api.model
    # def rent_done_cron(self):
    #     """Method to rent done cron."""
    #     rent_obj = self.env['fleet.rent']
    #     rent_sched_obj = self.env['tenancy.rent.schedule']
    #     for rent in rent_obj.search([('date_end', '!=', False),
    #                                  ('state', 'in', ['done', 'close'])]):
    #         records = []
    #         if rent.rent_schedule_ids:
    #             records = rent_sched_obj.search([
    #                 ('paid', '=', False),
    #                 ('id', 'in', rent.rent_schedule_ids.ids)])
    #         if not records:
    #             if datetime.now() >= rent.date_end:
    #                 reason = "This Rent Order is auto completed due to your "
    #                 "rent limit is over."
    #                 rent.write({'state': 'done',
    #                             'close_reson': reason,
    #                             'date_cancel': datetime.now(),
    #                             'cancel_by_id': self._uid})

    @api.model
    def rent_payment_done(self):
        """Method to send notification of rent done."""
        rent_obj = self.env['fleet.rent']
        rent_sched_obj = self.env['tenancy.rent.schedule']
        mail_temp_rec = self.env.ref('fleet_rent.email_rent_complete_template')
        for rent in rent_obj.search([('state', '=', 'open')]):
            records = []
            if rent.rent_schedule_ids:
                records = rent_sched_obj.search([
                    ('paid', '=', False),
                    ('fleet_rent_id', '=', rent.id)])
            if not records:
                mail_temp_rec.send_mail(rent.id, force_send=True)

    def action_rent_confirm(self):
        """Method to confirm rent status."""
        for rent in self:
            rent_vals = {'state': 'open'}
            if rent.rent_amt < 1:
                raise ValidationError("Rental Vehicle Rent amount should be greater than zero !! "
                                      "Please add 'Rental Vehicle Rent' amount !!")
            if not rent.name or rent.name == 'New':
                seq = self.env['ir.sequence'].next_by_code('fleet.rent')
                rent_vals.update({'name': seq})
            rent.write(rent_vals)

    def action_rent_close(self):
        """Method to Change rent state to close."""
        return {
            'name': ('Rent Close Form'),
            'res_model': 'rent.close.reason',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'
        }

    def action_rent_done(self):
        """Method to Change rent state to done."""
        rent_sched_obj = self.env['tenancy.rent.schedule']
        for rent in self:
            if not rent.rent_schedule_ids:
                raise ValidationError("Without Rent schedule you can not done the rent."
                                      "\nplease first create the rent schedule.")
            if rent.rent_schedule_ids:
                rent_schedule = rent_sched_obj.search([
                    ('paid', '=', False),
                    ('id', 'in', rent.rent_schedule_ids.ids)])
                if rent_schedule:
                    raise ValidationError("Scheduled Rents is remaining."
                                          "\nplease first pay scheduled rents.!!")
                rent.state = 'done'

    def action_set_to_draft(self):
        """Method to Change rent state to close."""
        for rent in self:
            if rent.state == 'open' and rent.rent_schedule_ids:
                raise Warning(_('You can not move rent to draft '
                                'stage because rent schedule is already created !!'))
            rent.state = 'draft'

    def action_set_to_renew(self):
        """Method to open rent renew wizard."""
        context = self.env.context
        context = dict(context)
        if context is None:
            context = {}
        for rent in self:
            rent.cr_rent_btn = False
            if rent.vehicle_id and rent.vehicle_id.state == 'write-off':
                raise Warning(_('You can not renew rent for %s \
                                because this vehicle is in \
                                write-off.') % (rent.vehicle_id.name))
            tenancy_rent_ids = self.env['tenancy.rent.schedule'].search(
                [('fleet_rent_id', '=', rent.id), ('state', 'in', ['draft', 'open'])])
            if tenancy_rent_ids:
                raise Warning(_('In order to Renew a Tenancy,'
                                'Please make all related Rent Schedule entries posted !!'))
            if rent.date_close:
                date = rent.date_close + timedelta(days=1)
            else:
                date = rent.date_end + timedelta(days=1)
            str_date = datetime.strftime(date, DTF)
            context.update({
                'default_start_date': date
            })
            return {
                'name': ('Tenancy Renew Wizard'),
                'res_model': 'renew.tenancy',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': context
            }

    def action_deposite_return(self):
        """Method to return deposite."""
        for rent in self:
            deposit_inv_ids = self.env['account.move'].search([
                ('fleet_rent_id', '=', rent.id), ('type', '=', 'out_refund'),
                ('state', 'in', ['draft', 'open', 'in_payment']),
                ('is_deposit_return_inv', '=', True)
            ])
            if deposit_inv_ids:
                raise Warning(_("Deposit Return invoice is already Pending\n"
                                "Please proceed that Return invoice first"))

            self.ensure_one()
            vehicle = rent.vehicle_id or False
            purch_journal = rent.env['account.journal'].search([
                ('type', '=', 'sale')], limit=1)
            if vehicle and not vehicle.expence_acc_id:
                raise Warning(_('Please Configure Expense Account in '
                                'Vehicle Registration form !!'))

            inv_line_values = {
                'name': 'Deposit Return' or "",
                'quantity': 1,
                'account_id': vehicle and vehicle.expence_acc_id and
                              vehicle.expence_acc_id.id or False,
                'price_unit': rent.deposit_amt or 0.00,
                'fleet_rent_id': rent.id,
            }
            invoice_id = rent.env['account.move'].create({
                'invoice_origin': 'Deposit Return For ' + rent.name or "",
                'type': 'out_refund',
                # 'property_id': vehicle and vehicle.id or False,
                'partner_id': rent.tenant_id and rent.tenant_id.partner_id.id or False,
                # 'account_id': rent.tenant_id and
                # rent.tenant_id.property_account_payable_id.id or False,
                'invoice_line_ids': [(0, 0, inv_line_values)],
                'invoice_date': datetime.now().strftime(DTF) or False,
                'fleet_rent_id': rent.id,
                'is_deposit_return_inv': True,
                'journal_id': purch_journal and purch_journal.id or False,
            })

            rent.write({'invoice_id': invoice_id.id})
        return True

    def action_deposite_receive(self):
        """Method to open the related payment form view."""
        for rent in self:

            if rent.deposit_amt < 1:
                raise Warning(_("Deposit amount should not be zero.\n"
                                "Please Enter Deposit Amount."))

            deposit_inv_ids = self.env['account.move'].search([
                ('fleet_rent_id', '=', rent.id), ('type', '=', 'out_invoice'),
                ('state', 'in', ['draft', 'open', 'in_payment']),
                ('is_deposit_inv', '=', True)])
            if deposit_inv_ids:
                raise Warning(_("Deposit invoice is already Pending\n"
                                "Please proceed that deposit invoice first"))

            inv_line_values = {
                'name': 'Deposit Receive' or "",
                # 'origin': rent.name or "",
                'quantity': 1,
                # 'account_id': rent.vehicle_id and rent.vehicle_id.expence_acc_id and
                # rent.vehicle_id.expence_acc_id.id or False,
                'price_unit': rent.deposit_amt or 0.00,
                'fleet_rent_id': rent.id,
            }
            invoice_id = rent.env['account.move'].create({
                'type': 'out_invoice',
                'partner_id': rent.tenant_id and rent.tenant_id.partner_id.id or False,
                'invoice_line_ids': [(0, 0, inv_line_values)],
                'invoice_date': datetime.now().strftime(DTF) or False,
                'fleet_rent_id': rent.id,
                'is_deposit_inv': True,
            })
            rent.write({'invoice_id': invoice_id.id})
            return True

    def create_rent_schedule(self):
        """Method to create rent schedule Lines."""
        for rent in self:
            for rent_line in rent.rent_schedule_ids:
                if not rent_line.paid and not rent_line.move_check:
                    raise Warning(_('You can\'t create new rent '
                                    'schedule Please make all related Rent Schedule '
                                    'entries paid.'))
            rent_obj = self.env['tenancy.rent.schedule']
            currency = rent.currency_id or False
            tenent = rent.tenant_id or False
            vehicle = rent.vehicle_id or False
            if rent.date_start and rent.rent_type_id and \
                    rent.rent_type_id.renttype:
                interval = int(rent.rent_type_id.duration)
                date_st = rent.date_start
                if rent.rent_type_id.renttype == 'Months':
                    for i in range(0, interval):
                        date_st = date_st + relativedelta(months=int(1))
                        rent_obj.create({
                            'start_date': date_st.strftime(DTF),
                            'amount': rent.rent_amt,
                            'pen_amt': rent.rent_amt,
                            'vehicle_id': vehicle and vehicle.id or False,
                            'fleet_rent_id': rent.id,
                            'currency_id': currency and currency.id or False,
                            'rel_tenant_id': tenent and tenent.id or False
                        })
                if rent.rent_type_id.renttype == 'Years':
                    for i in range(0, interval):
                        date_st = date_st + relativedelta(years=int(1))
                        rent_obj.create({
                            'start_date': date_st.strftime(DTF),
                            'amount': rent.rent_amt,
                            'vehicle_id': vehicle and vehicle.id or False,
                            'fleet_rent_id': rent.id,
                            'currency_id': currency and currency.id or False,
                            'rel_tenant_id': tenent and tenent.id or False
                        })
                if rent.rent_type_id.renttype == 'Weeks':
                    for i in range(0, interval):
                        date_st = date_st + relativedelta(weeks=int(1))
                        rent_obj.create({
                            'start_date': date_st.strftime(DTF),
                            'amount': rent.rent_amt,
                            'vehicle_id': vehicle and vehicle.id or False,
                            'fleet_rent_id': rent.id,
                            'currency_id': currency and currency.id or False,
                            'rel_tenant_id': tenent and tenent.id or False
                        })
                if rent.rent_type_id.renttype == 'Days':
                    rent_obj.create({
                        'start_date': date_st.strftime(DTF),
                        'amount': rent.rent_amt * interval,
                        'vehicle_id': vehicle and vehicle.id or False,
                        'fleet_rent_id': rent.id,
                        'currency_id': currency and currency.id or False,
                        'rel_tenant_id': tenent and tenent.id or False
                    })
                if rent.rent_type_id.renttype == 'Hours':
                    rent_obj.create({
                        'start_date': date_st.strftime(DTF),
                        'amount': rent.rent_amt * interval,
                        'vehicle_id': vehicle and vehicle.id or False,
                        'fleet_rent_id': rent.id,
                        'currency_id': currency and currency.id or False,
                        'rel_tenant_id': tenent and tenent.id or False
                    })
                # cr_rent_btn is used to hide rent schedule button.
                rent.cr_rent_btn = True
        return True


class RentType(models.Model):
    """Rent Type Model."""

    _name = "rent.type"
    _description = 'Vehicle Rent Type'

    @api.model
    def create(self, vals):
        """Overridden Method."""
        if vals.get('duration') < 1:
            raise ValidationError("You Can't Enter Duration Less "
                                  "Than One(1).")
        return super(RentType, self).create(vals)

    @api.depends('duration', 'renttype')
    def name_get(self):
        """Name get Method."""
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
        """Name Search Method."""
        args += ['|', ('duration', operator, name),
                 ('renttype', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()

    @api.onchange('duration', 'renttype')
    def onchange_renttype_name(self):
        """Onchange Rent Type Name."""
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
    """Maintenace Type Model."""

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
    """Maintenace Cost Model."""

    _name = 'maintenance.cost'
    _description = 'Vehicle Maintenance Cost'

    maint_type = fields.Many2one('maintenance.type',
                                 string='Maintenance Type')
    cost = fields.Float(string='Maintenance Cost',
                        help='insert the cost')
    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle')
    tenant_id = fields.Many2one(related='fleet_rent_id.tenant_id',
                                string='Tenant User', store=True,
                                help="Tenant Name of Rental Vehicle.")
    fleet_tenant_id = fields.Many2one("res.partner",
                                      string='Fleet Tenant',
                                      help="Tenant Name of Rental Vehicle.")

    @api.onchange('maint_type')
    def onchange_maint_type(self):
        """Method is used to set maintenance type related.

        Fields value on change of property.
        """
        if self.maint_type:
            self.cost = self.maint_type.cost or 0.00


class TenancyRentSchedule(models.Model):
    """Tenancy Rent Schedule."""

    _name = "tenancy.rent.schedule"
    _description = 'Tenancy Rent Schedule'
    _rec_name = "fleet_rent_id"
    _order = 'start_date'

    @api.depends('move_id')
    def _compute_get_move_check(self):
        for rent_sched in self:
            rent_sched.move_check = bool(rent_sched.move_id)

    note = fields.Text(string='Notes', help='Additional Notes.')
    currency_id = fields.Many2one('res.currency',
                                  string='Currency')
    amount = fields.Float(string='Amount', default=0.0,
                          currency_field='currency_id', help="Rent Amount.")
    start_date = fields.Datetime(string='Date', help='Start Date.')
    end_date = fields.Date(string='End Date', help='End Date.')
    cheque_detail = fields.Char(string='Cheque Detail', size=30)
    move_check = fields.Boolean(compute='_compute_get_move_check', string='Posted',
                                store=True)
    rel_tenant_id = fields.Many2one('res.users',
                                    string="Tenant")
    move_id = fields.Many2one('account.move',
                              string='Depreciation Entry')
    vehicle_id = fields.Many2one('fleet.vehicle',
                                 string='Vehicle', help='Vehicle Name.')
    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle',
                                    help='Rental Vehicle Name.')
    # state = fields.Selection(related='fleet_rent_id.state', string='Status')
    paid = fields.Boolean(string='Paid',
                          help="True if this rent is paid by tenant")
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'),
                              ('paid', 'Paid'), ('cancel', 'Cancel')], string="State", default="draft")
    invc_id = fields.Many2one('account.move', string='Invoice')
    inv = fields.Boolean(string='Is Invoice?')
    pen_amt = fields.Float(string='Pending Amount', help='Pending Amount.')

    def create_invoice(self):
        """Create invoice for Rent Schedule."""
        self.ensure_one()
        journal_id = self.env['account.journal'].search([
            ('type', '=', 'sale')], limit=1)
        rent = self.fleet_rent_id or False
        vehicle = rent and rent.vehicle_id or False
        if vehicle and not vehicle.income_acc_id:
            raise Warning(_('Please Configure Income Account from Vehicle !!'))
        inv_line_main = {
            'name': 'Maintenance cost',
            'price_unit': rent and rent.maintenance_cost or 0.00,
            'quantity': 1,
            # 'account_id': rent.vehicle_id.income_acc_id.id or False,
        }
        inv_line_values = {
            # 'origin': 'tenancy.rent.schedule',
            'name': 'Tenancy(Rent) Cost',
            'price_unit': self.amount or 0.00,
            'quantity': 1,
            # 'account_id': vehicle and vehicle.income_acc_id.id or False,
        }
        inv_values = {
            'partner_id': rent and rent.tenant_id and
                          rent.tenant_id.partner_id and
                          rent.tenant_id.partner_id.id or False,
            'type': 'out_invoice',
            'vehicle_id': vehicle and vehicle.id or False,
            'invoice_date': datetime.now().strftime(DF) or False,
            'journal_id': journal_id and journal_id.id or False,
            # 'account_id': rent and rent.tenant_id and
            # rent.tenant_id.property_account_receivable_id and
            # rent.tenant_id.property_account_receivable_id.id or False,
            'fleet_rent_id': rent and rent.id or False,
        }
        if self.fleet_rent_id and self.fleet_rent_id.maintenance_cost:
            inv_values.update({'invoice_line_ids': [(0, 0, inv_line_values),
                                                    (0, 0, inv_line_main)]})
        else:
            inv_values.update(
                {'invoice_line_ids': [(0, 0, inv_line_values)]})
        acc_id = self.env['account.move'].create(inv_values)
        self.write({'invc_id': acc_id.id, 'inv': True})
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'view_move_form')[1]

        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    def open_invoice(self):
        """Method Open Invoice."""
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'view_move_form')[1]
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }

    def create_move(self):
        """
        Button Method is used to create account move.

        @param self: The object pointer.
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
                # 'account_id':
                # line.tenancy_id.property_id.income_acc_id.id or False,
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
                # 'account_id':
                # line.tenancy_id.tenant_id.property_account_receivable_id.id,
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

    @api.model
    def rent_remainder_cron(self):
        """Method to remainder rent."""
        mail_temp_rec = self.env.ref(
            'fleet_rent.email_rent_remainder_template')
        tenancy_rent_recs = self.search([
            ('state', '!=', 'paid'),
            ('start_date', '<=', fields.Datetime.now())
        ])
        if tenancy_rent_recs and mail_temp_rec:
            for pending_rent in tenancy_rent_recs:
                mail_temp_rec.send_mail(pending_rent.id, force_send=True)
