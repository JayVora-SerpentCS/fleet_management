# See LICENSE file for full copyright and licensing details.
"""Asset Model."""

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, except_orm
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, misc


class AccountMove(models.Model):
    """Account Move."""

    _inherit = "account.move"
    _description = "Account Entry"

    asset_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        help='Vehicle')
    schedule_date = fields.Date(
        string='Schedule Date',
        help='Rent Schedule Date.')
    source = fields.Char(
        string='Source',
        help='Source from where account move created.')

    @api.multi
    def assert_balanced(self):
        """Method Assert Balanced."""
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')
        self._cr.execute("""\
            SELECT      move_id
            FROM        account_move_line
            WHERE       move_id in %s
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > %s
            """, (tuple(self.ids), 10 ** (-max(5, prec))))
        self._cr.fetchall()
        if len(self._cr.fetchall()) != 0:
            raise ValidationError(_("Cannot create unbalanced journal entry."))
        return True


class AccountAssetAsset(models.Model):
    """Account Asset Asset."""

    _inherit = 'account.asset.asset'
    _description = 'Asset'

    @api.multi
    @api.depends('image')
    def _has_image(self):
        """
        Method is used to set Property image.

        @param self: The object pointer.

        @return: True or False.
        """
        result = False
        for p in self:
            if p.image:
                result = bool(p.image)
            p.has_image = result

    @api.multi
    @api.depends('tenancy_property_ids', 'tenancy_property_ids.date',
                 'tenancy_property_ids.date_start')
    def occupancy_calculation(self):
        """
        Method is used to calculate occupancy rate.

        @param self: The object pointer.

        @return: Calculated Occupancy Rate.
        """
        occ_rate = 0
        diffrnc = 0
        for prop_rec in self:
            if prop_rec.date:
                prop_date = datetime.strptime(
                    str(prop_rec.date), DEFAULT_SERVER_DATE_FORMAT).date()
                pur_diff = datetime.now().date() - prop_date
                purchase_diff = pur_diff.days
                if prop_rec.tenancy_property_ids and \
                        prop_rec.tenancy_property_ids.ids:
                    for tency_rec in prop_rec.tenancy_property_ids:
                        if tency_rec.date and tency_rec.date_start:
                            date_diff = \
                                datetime.strptime(
                                    tency_rec.date,
                                    DEFAULT_SERVER_DATETIME_FORMAT) - \
                                datetime.strptime(
                                    tency_rec.date_start,
                                    DEFAULT_SERVER_DATETIME_FORMAT)
                            diffrnc += date_diff.days
                if purchase_diff != 0 and diffrnc != 0:
                    occ_rate = (purchase_diff * 100) / diffrnc
                prop_rec.occupancy_rates = occ_rate

    @api.multi
    @api.depends('maintenance_ids', 'maintenance_ids.cost',
                 'tenancy_property_ids', 'tenancy_property_ids.rent')
    def roi_calculation(self):
        """
        Method is used to Calculate ROI(Return On Investment).

        @param self: The object pointer.

        @return: Calculated Return On Investment.
        """
        cost_of_investment = 0
        gain_from_investment = 0
        total = 0
        for prop_rec in self:
            if prop_rec.maintenance_ids and prop_rec.maintenance_ids.ids:
                for maintenance in prop_rec.maintenance_ids:
                    cost_of_investment += maintenance.cost
            if prop_rec.tenancy_property_ids and \
                    prop_rec.tenancy_property_ids.ids:
                for gain in prop_rec.tenancy_property_ids:
                    gain_from_investment += gain.rent
            if (cost_of_investment != 0 and gain_from_investment != 0 and
                    cost_of_investment != gain_from_investment):
                total = (gain_from_investment - cost_of_investment) / \
                    cost_of_investment
            prop_rec.roi = total

    @api.one
    @api.depends('roi')
    def ten_year_roi_calculation(self):
        """
        Method is used to Calculate ten years ROI(Return On Investment).

        @param self: The object pointer.

        @return: Calculated Return On Investment.
        """
        self.ten_year_roi = 10 * self.roi

    @api.multi
    @api.depends('tenancy_property_ids',
                 'tenancy_property_ids.rent_schedule_ids')
    def cal_simulation(self):
        """
        Method is used to calculate simulation.

        which is used in Financial Performance Report.

        @param self: The object pointer.

        @return: Calculated Simulation Amount.
        """
        amt = 0.0
        for property_data in self:
            if property_data.tenancy_property_ids and \
                    property_data.tenancy_property_ids.ids:
                for tncy in property_data.tenancy_property_ids:
                    if tncy.rent_schedule_ids and tncy.rent_schedule_ids.ids:
                        for prty_tncy_data in tncy.rent_schedule_ids:
                            amt += prty_tncy_data.amount
            property_data.simulation = amt

    @api.multi
    @api.depends('tenancy_property_ids',
                 'tenancy_property_ids.rent_schedule_ids',
                 'tenancy_property_ids.rent_schedule_ids.move_check')
    def cal_revenue(self):
        """
        Method is used to calculate revenue.

        which is used in Financial Performance Report.

        @param self: The object pointer.

        @return: Calculated Revenue Amount.
        """
        amt = 0.0
        for property_data in self:
            if property_data.tenancy_property_ids and \
                    property_data.tenancy_property_ids.ids:
                for tncy in property_data.tenancy_property_ids:
                    if tncy.rent_schedule_ids and tncy.rent_schedule_ids.ids:
                        for prty_tncy_data in tncy.rent_schedule_ids:
                            if prty_tncy_data.move_check is True:
                                amt += prty_tncy_data.amount
            property_data.revenue = amt

    @api.one
    @api.depends('salvage_value', 'depreciation_line_ids')
    def _amount_residual(self):
        """
        @param self: The object pointer.

        @return: Calculated Residual Amount.
        """
        total_amount = 0.0
        total_residual = 0.0
        for rec in self:
            if rec.value_residual > 0:
                for line in rec.depreciation_line_ids:
                    if line.move_check:
                        total_amount += line.amount
                total_residual = \
                    rec.value_residual - total_amount - rec.salvage_value
            rec.value_residual = total_residual

    @api.one
    @api.depends('gfa_feet', 'unit_price')
    def cal_total_price(self):
        """
        Method is used to Calculate Total Price.

        @param self: The object pointer.

        @return: Calculated Total Price.
        """
        self.total_price = self.gfa_feet * self.unit_price

    date = fields.Date(string='Date', required=True,
                       readonly=True, default=fields.Date.context_today)
    image = fields.Binary(
        string='Image')
    simulation_date = fields.Date(
        string='Simulation Date',
        help='Simulation Date.')
    age_of_property = fields.Date(
        string='Property Creation Date',
        default=fields.Date.context_today,
        help='Property Creation Date.')
    city = fields.Char(
        string='City')
    street = fields.Char(
        string='Street')
    street2 = fields.Char(
        string='Street2')
    township = fields.Char(
        string='Township')
    simulation_name = fields.Char(
        string='Simulation Name')
    construction_cost = fields.Char(
        string='Construction Cost')
    zip = fields.Char(
        string='Zip',
        size=24,
        change_default=True)
    video_url = fields.Char(
        string='Video URL',
        help="//www.youtube.com/embed/mwuPTI8AT7M?rel=0")
    unit_price = fields.Float(
        string='Unit Price',
        help='Unit Price Per Sqft.')
    ground_rent = fields.Float(
        string='Ground Rent',
        help='Ground rent of Property.')
    gfa_meter = fields.Float(
        string='GFA(m)',
        help='Gross floor area in Meter.')
    sale_price = fields.Float(
        string='Sale Price',
        help='Sale price of the Property.')
    gfa_feet = fields.Float(
        string='GFA(Sqft)',
        help='Gross floor area in Square feet.')
    ten_year_roi = fields.Float(
        string="10year ROI",
        compute='ten_year_roi_calculation',
        help="10year Return of Investment.")
    roi = fields.Float(
        string="ROI",
        compute='roi_calculation',
        store=True,
        help='ROI ( Return On Investment ) = ( Total Tenancy rent - Total \
        maintenance cost ) / Total maintenance cost.',)
    occupancy_rates = fields.Float(
        string="Occupancy Rate",
        store=True,
        compute='occupancy_calculation',
        help='Total Occupancy rate of Property.')
    value_residual = fields.Float(
        string='Residual Value',
        method=True,
        compute='_amount_residual',
        digits=dp.get_precision('Account'),)
    simulation = fields.Float(
        string='Total Amount',
        compute='cal_simulation',
        store=True)
    revenue = fields.Float(
        string='Revenue',
        compute='cal_revenue',
        store=True)
    total_price = fields.Float(
        string='Total Price',
        compute='cal_total_price',
        help='Total Price of Property, \nTotal Price = Unit Price * \
        GFA (Sqft).')
    has_image = fields.Boolean(
        compute='_has_image')
    pur_instl_chck = fields.Boolean(
        string='Purchase Installment Check',
        default=False)
    sale_instl_chck = fields.Boolean(
        string='Sale Installment Check',
        default=False)
    color = fields.Integer(
        string='Color',
        default=4)
    floor = fields.Integer(
        string='Floor',
        help='Number of Floors.')
    no_of_towers = fields.Integer(
        string='No of Towers',
        help='Number of Towers.')
    no_of_property = fields.Integer(
        string='Property Per Floors.',
        help='Number of Properties Per Floor.')
    income_acc_id = fields.Many2one(
        comodel_name='account.account',
        string='Property Income Account',
        help='Income Account of Property.')
    expense_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Expense Account',
        help='Expense Account of Property.')
    parent_id = fields.Many2one(
        comodel_name='account.asset.asset',
        string='Parent Property')
    current_tenant_id = fields.Many2one(
        comodel_name='res.partner',
        string='Current Tenant')
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        ondelete='restrict')
    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='State ',
        ondelete='restrict')
    analytic_acc_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account')
    rent_type_id = fields.Many2one(
        comodel_name='rent.type',
        string='Rent Type',
        help='Type of Rent.')
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact Name')
    property_manager = fields.Many2one(
        comodel_name='res.partner',
        string='Property Manager/Owner')
    maintenance_ids = fields.One2many(
        comodel_name='property.maintenance',
        inverse_name='property_id',
        string='Maintenance')
    child_ids = fields.One2many(
        comodel_name='account.asset.asset',
        inverse_name='parent_id',
        string='Children Assets')
    tenancy_property_ids = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='vehicle_property_id',
        string='Tenancy Property')
    account_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='asset_id',
        string='Entries',
        readonly=True,
        states={'draft': [('readonly', False)]})
    depreciation_line_ids = fields.One2many(
        comodel_name='account.asset.depreciation.line',
        inverse_name='asset_id',
        string='Depreciation Lines',
        readonly=True,
        states={'draft': [('readonly', False)]})
    bedroom = fields.Selection(
        [('1', '1'), ('2', '2'),
         ('3', '3'), ('4', '4'),
         ('5', '5+')],
        string='Bedrooms',
        default='1')
    bathroom = fields.Selection(
        [('1', '1'), ('2', '2'),
         ('3', '3'), ('4', '4'),
         ('5', '5+')],
        string='Bathrooms',
        default='1')
    facing = fields.Selection(
        [('north', 'North'), ('south', 'South'),
         ('east', 'East'), ('west', 'West')],
        string='Facing',
        default='east')
    furnished = fields.Selection(
        [('none', 'None'),
         ('semi_furnished', 'Semi Furnished'),
         ('full_furnished', 'Full Furnished')],
        string='Furnishing',
        default='none',
        help='Furnishing.')
    state = fields.Selection(
        [('new_draft', 'Booking Open'),
         ('draft', 'Available'),
         ('book', 'Booked'),
         ('normal', 'On Lease'),
         ('close', 'Sale'),
         ('sold', 'Sold'),
         ('cancel', 'Cancel')],
        string='State',
        required=True,
        default='draft')
    rent_type_id = fields.Many2one(
        comodel_name='rent.type',
        string='Rent Type')

    @api.model
    def create(self, vals):
        """
        Method is used to overrides orm create method.

        @param self: The object pointer.

        @param vals: dictionary of fields value.
        """
        if not vals:
            vals = {}
        if 'message_follower_ids' in vals:
            del vals['message_follower_ids']
        vals['code'] = self.env['ir.sequence'].next_by_code('property')
        if vals.get('parent_id'):
            parent_periods = self.browse(vals.get('parent_id'))
            if parent_periods.rent_type_id and parent_periods.rent_type_id.id:
                vals.update({'rent_type_id': parent_periods.rent_type_id.id})
        acc_analytic_id = self.env['account.analytic.account'].sudo()
        acc_analytic_id.create({'name': vals['name']})
        return super(AccountAssetAsset, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Method is used to overrides orm write method.

        @param self: The object pointer.

        @param vals: dictionary of fields value.
        """
        if 'state' in vals and vals['state'] == 'new_draft':
            vals.update({'color': 0})
        if 'state' in vals and vals['state'] == 'draft':
            vals.update({'color': 4})
        if 'state' in vals and vals['state'] == 'book':
            vals.update({'color': 2})
        if 'state' in vals and vals['state'] == 'normal':
            vals.update({'color': 7})
        if 'state' in vals and vals['state'] == 'close':
            vals.update({'color': 9})
        if 'state' in vals and vals['state'] == 'sold':
            vals.update({'color': 9})
        if 'state' in vals and vals['state'] == 'cancel':
            vals.update({'color': 1})
        return super(AccountAssetAsset, self).write(vals)

    @api.onchange('parent_id')
    def parent_property_onchange(self):
        """
        Method will change.

        address fields values accordingly.

        @param self: The object pointer.
        """
        if self.parent_id:
            self.street = self.parent_id.street or ''
            self.street2 = self.parent_id.street2 or ''
            self.township = self.parent_id.township or ''
            self.city = self.parent_id.city or ''
            self.state_id = self.parent_id.state_id.id or False
            self.zip = self.parent_id.zip or ''
            self.country_id = self.parent_id.country_id.id or False

    @api.onchange('gfa_feet')
    def sqft_to_meter(self):
        """
        Method will change.

        GFA Meter field value accordingly.

        @param self: The object pointer.

        @return: Calculated GFA Feet.
        """
        meter_val = 0.0
        if self.gfa_feet:
            meter_val = float(self.gfa_feet / 10.7639104)
        self.gfa_meter = meter_val

    @api.onchange('unit_price', 'gfa_feet')
    def unit_price_calc(self):
        """
        Unit Price and GFA Feet fields value.

        Method will change Total Price and Purchase Value.

        accordingly.

        @param self: The object pointer
        """
        if self.unit_price and self.gfa_feet:
            self.total_price = float(self.unit_price * self.gfa_feet)
            self.value = float(self.unit_price * self.gfa_feet)
        if self.unit_price and not self.gfa_feet:
            raise ValidationError(_('Please Insert GFA(Sqft) Please'))

    @api.multi
    def edit_status(self):
        """
        Method is used to change property state to book.

        @param self: The object pointer.
        """
        for rec in self:
            if not rec.property_manager:
                raise ValidationError(_('Please Insert Owner Name'))

        return self.write({'state': 'book'})

    @api.multi
    def edit_status_book(self):
        """
        Method will open a wizard.

        @param self: The object pointer.
        """
        cr, uid, context = self.env.args
        context = dict(context)
        for rec in self:
            context.update({'edit_result': rec.id})
            self.env.args = cr, uid, misc.frozendict(context)
        return {
            'name': ('wizard'),
            'res_model': 'book.available',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_current_ids': context.get('edit_result')},
        }

    @api.multi
    def open_url(self):
        """
        Button method is used to open a URL.

        according fields values.

        @param self: The object pointer.
        """
        for property_brw in self:
            if property_brw.street:
                address_path = \
                    (property_brw.street and
                     (property_brw.street + ',') or ' ') + \
                    (property_brw.street2 and (
                        property_brw.street2 + ',') or ' ') + \
                    (property_brw.city and (
                        property_brw.city + ',') or ' ') + \
                    (property_brw.state_id.name and (
                        property_brw.state_id.name + ',') or ' ') + \
                    (property_brw.country_id.name and (
                        property_brw.country_id.name + ',') or ' ')
                rep_address = address_path.replace(' ', '+')
                url = "http://maps.google.com/?q=%s&ie=UTF8&z=18" % (
                    rep_address)
                return {
                    'name': 'Go to website',
                    'res_model': 'ir.actions.act_url',
                    'type': 'ir.actions.act_url',
                    'target': 'current',
                    'url': url
                }
            else:
                raise except_orm(
                    ('No Address!'), ('No Address created for this Property!'))
        return True

    @api.multi
    def button_normal(self):
        """
        Button method is used to change property state to On Lease.

        @param self: The object pointer.
        """
        return self.write({'state': 'normal'})

    @api.multi
    def button_sold(self):
        """
        Button method is used to change property state to Sold.

        @param self: The object pointer.
        """
        data = self
        if not data.expense_account_id:
            raise Warning(_('Please Configure Income Account from Property'))
        inv_line_values = {
            'name': data.name or "",
            'origin': 'account.asset.asset',
            'quantity': 1,
            'account_id': data.income_acc_id and data.income_acc_id.id or False,
            'price_unit': data.sale_price or 0.00,
        }

        inv_values = {
            'origin': data.name or "",
            'type': 'out_invoice',
            'property_id': data.id,
            'partner_id': data.customer_id.id or False,
            'payment_term_id': data.payment_term.id,
            'invoice_line_ids': [(0, 0, inv_line_values)],
            'date_invoice': datetime.now().strftime(
                DEFAULT_SERVER_DATE_FORMAT) or False,
            'number': data.code or '',
        }
        self.env['account.invoice'].create(inv_values)
        data.write({'state': 'sold'})
        return True

    @api.multi
    def button_close(self):
        """
        Button method is used to change property state to Sale.

        @param self: The object pointer.
        """
        return self.write({'state': 'close'})

    @api.multi
    def button_cancel(self):
        """
        Button method is used to change property state to Cancel.

        @param self: The object pointer.
        """
        return self.write({'state': 'cancel'})

    @api.multi
    def button_draft(self):
        """
        Button method is used to change property state to Available.

        @param self: The object pointer.
        """
        return self.write({'state': 'draft'})

    @api.multi
    def date_addition(self, starting_date, end_date, period):
        """Method to date."""
        date_list = []
        if period == 'monthly':
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((datetime.strptime(
                        starting_date, DEFAULT_SERVER_DATE_FORMAT) +
                        relativedelta(months=1)).strftime(
                            DEFAULT_SERVER_DATE_FORMAT))
                starting_date = res
            return date_list
        else:
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((datetime.strptime(starting_date,
                                          DEFAULT_SERVER_DATE_FORMAT) +
                        relativedelta(years=1)).strftime(
                            DEFAULT_SERVER_DATE_FORMAT))
                starting_date = res
            return date_list
