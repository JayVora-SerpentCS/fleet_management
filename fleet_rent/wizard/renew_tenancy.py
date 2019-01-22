# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo.tools import misc
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT


class WizardRenewTenancy(models.TransientModel):
    _name = 'renew.tenancy'
    _description = 'Vehicle Renew Tenacy'

    start_date = fields.Datetime(
        string='Start Date')
    end_date = fields.Datetime(
        compute='_create_date',
        store=True,
        string='End Date')
    rent_type_id = fields.Many2one(
        comodel_name='rent.type',
        string='Rent Type',
        required=True)

    @api.multi
    @api.depends('rent_type_id', 'start_date')
    def _create_date(self):
        for rec in self:
            if rec.rent_type_id and rec.start_date:
                if rec.rent_type_id.renttype == 'Months':
                    rec.end_date = \
                        datetime.strptime(rec.start_date, DT) + \
                        relativedelta(months=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Years':
                    rec.end_date = datetime.strptime(rec.start_date, DT) + \
                            relativedelta(years=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Weeks':
                    rec.end_date = datetime.strptime(rec.start_date, DT) + \
                            relativedelta(weeks=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Days':
                    rec.end_date = datetime.strptime(str(rec.start_date), DT) + \
                            relativedelta(days=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Hours':
                    rec.end_date = datetime.strptime(rec.start_date, DT) + \
                            relativedelta(hours=int(rec.rent_type_id.duration))
        return True

    @api.constrains('start_date', 'end_date')
    def check_date_overlap(self):
        """
        This is a constraint method used to check the from date smaller than
        the Exiration date.
        @param self : object pointer
        """
        for ver in self:
            if ver.start_date and ver.end_date:
                dt_from = ver.start_date.strftime(DT)
                dt_to = ver.end_date.strftime(DT)
                if dt_to < dt_from:
                    raise ValidationError(
                        'End Date Should Be Greater Than Start Date!')

    @api.multi
    def renew_contract(self):
        """
                This Button Method is used to Renew Tenancy.
        @param self: The object pointer
        @return: Dictionary of values.
        """
        cr, uid, context = self.env.args
        context = dict(context)
        if context is None:
            context = {}
        modid = self.env['ir.model.data'].get_object_reference(
            'fleet_rent', 'property_analytic_view_form')
        if context.get('active_ids', []):
            for rec in self:
                start_d = datetime.strptime(
                    str(rec.start_date), DT)
                end_d = datetime.strptime(
                    str(rec.end_date), DT)
                if start_d > end_d:
                    raise Warning(
                        _('Please Insert End Date Greater Than Start Date'))
                act_prop = self.env['account.analytic.account'].browse(
                    context['active_ids'])
                act_prop.write({
                    'date_start': rec.start_date,
                    'date': rec.end_date,
                    'rent_type_id': rec.rent_type_id and
                    rec.rent_type_id.id or False,
                    'state': 'draft',
                    'rent_entry_chck': False,
                })
        self.env.args = cr, uid, misc.frozendict(context)
        return {
            'view_mode': 'form',
            'view_id': modid[1],
            'view_type': 'form',
            'res_model': 'account.analytic.account',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': context['active_ids'][0],
        }
