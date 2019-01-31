# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class VehicleChangeHistory(models.TransientModel):
    _name = 'vehicle.change.history'

    fleet_id = fields.Many2one('fleet.vehicle', string='Vehicle-ID')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    @api.multi
    def print_report(self):
        for rec in self:
            if not rec.date_from and not rec.date_to and not rec.fleet_id:
                raise Warning(_("User Error!\n 'Please select criteria \
                         to create Vehicle Change History Report!"))
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise Warning(_("User Error!\n Date To' must \
                            be greater than 'Date From'!"))
            date_range = {
                'date_from': rec.date_from,
                'date_to': rec.date_to,
                'fleet_id': rec.fleet_id and rec.fleet_id.id or False
            }
            datas = {
                'form': date_range,
            }
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'vehicle.change.history.xls',
                'datas': datas
            }
