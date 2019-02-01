# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class RepairLineSummary(models.TransientModel):
    _name = 'repair.line.summary'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    @api.multi
    def print_report(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise Warning(_("User Error!\n'Date To' must be \
                                greater than 'Date From' !"))
            date_range = {
                'date_from': rec.date_from,
                'date_to': rec.date_to,
            }
            datas = {
                'form': date_range,
            }
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'repair.line.summary.xls',
                    'datas': datas
                    }
