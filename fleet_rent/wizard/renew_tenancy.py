# See LICENSE file for full copyright and licensing details.
"""Renew Tenancy Wizard."""

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT as DT


class WizardRenewTenancy(models.TransientModel):
    """Wizard Renew Tenancy."""

    _name = 'renew.tenancy'
    _description = 'Vehicle Renew Tenacy'

    @api.depends('rent_type_id', 'start_date')
    def _create_date(self):
        for rec in self:
            if rec.rent_type_id and rec.start_date:
                if rec.rent_type_id.renttype == 'Months':
                    rec.end_date = rec.start_date + \
                        relativedelta(months=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Years':
                    rec.end_date = rec.start_date + \
                        relativedelta(years=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Weeks':
                    rec.end_date = rec.start_date + \
                        relativedelta(weeks=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Days':
                    rec.end_date = rec.start_date \
                        + relativedelta(days=int(rec.rent_type_id.duration))
                if rec.rent_type_id.renttype == 'Hours':
                    rec.end_date = rec.start_date + \
                        relativedelta(hours=int(rec.rent_type_id.duration))
        return True

    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(compute='_create_date',
                               string='End Date', store=True)
    rent_type_id = fields.Many2one('rent.type',
                                   string='Rent Type', required=True)

    @api.constrains('start_date', 'end_date')
    def check_date_overlap(self):
        """Method used to check the date."""
        for ver in self:
            if ver.start_date and ver.end_date:
                dt_from = ver.start_date.strftime(DT)
                dt_to = ver.end_date.strftime(DT)
                if dt_to < dt_from:
                    raise ValidationError(
                        'End Date Should Be Greater Than Start Date!')

    @api.multi
    def renew_contract(self):
        """Button Method is used to Renew Tenancy."""
        view_id = self.env['ir.model.data'].get_object_reference(
            'fleet_rent', 'view_fleet_rent_form')
        if self._context.get('active_id', False):
            for rec in self:
                if rec.start_date > rec.end_date:
                    raise Warning(_('Please Insert End Date \
                        Greater Than Start Date !!'))
                rent_rec = self.env['fleet.rent'].browse(self._context['active_id'])
                for rent in rent_rec:
                    if rent.date_close and rec.start_date:
                        if rec.start_date < rent.date_close:
                            raise Warning('Start Date should be Greater Than Rent Close Date.')
                    elif rent.date_end and rec.start_date:
                        if rec.start_date < rent.date_end:
                            raise Warning('Start Date should be Greater Than Rent Expiration Date.')
                rent = rent_rec.copy()
                rent.write({
                    'rent_type_id': rec.rent_type_id and rec.rent_type_id.id or False,
                    'name': 'New'
                })

        return {
            'view_id': view_id and len(view_id) >= 2 and view_id[1] or False,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'fleet.rent',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': rent.id,
        }
