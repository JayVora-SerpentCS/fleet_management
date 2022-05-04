# See LICENSE file for full copyright and licensing details.
"""Repair line summary."""

import time
from datetime import datetime
from odoo.tools import format_date
from odoo import _, api, models
from odoo.exceptions import UserError


class RepairLineSummary(models.AbstractModel):
    """Repair Line Summary."""

    _name = 'report.fleet_operations.repair_line_summary_qweb'
    _description = 'Repair Line Summary Report'

    def get_repair_line_detail(self, date_range):
        """Method to get repair line detail print report."""
        work_order_obj = self.env['fleet.vehicle.log.services']
        start = date_range.get('date_from')
        end = date_range.get('date_to')
        work_order_ids = \
            work_order_obj.search([('date', '>=', start),
                                   ('date', '<=', end),
                                   ('state', '=', 'done')])
        repair_line_data = []
        repair_l_dic = {}
        if not work_order_ids:
            raise UserError(_("Warning! No Work order found between the selected date !!"))
        if work_order_ids:
            for work_rec in work_order_ids:
                for repair_l in work_rec.repair_line_ids.filtered(lambda r: r.complete):
                    rep_type = repair_l.repair_type_id
                    if rep_type and rep_type.name:
                        if repair_l_dic.get(rep_type.id, False):
                            repair_l_dic[rep_type.id]['count'] += 1
                        else:
                            date = format_date(self.env, work_rec.date, self._context.get('lang'), date_format=False)
                            repair_l_dic[rep_type.id] = {
                                'repair_type': repair_l.repair_type_id.name or '',
                                'count': 1,
                                'vehicle_name': work_rec.fmp_id,
                                'issue_date': date if date else False,
                            }
        for repair_data in repair_l_dic.keys():
            if repair_data:
                repair_line_data.append(repair_l_dic[repair_data])
        if repair_line_data:
            repair_line_data = sorted(repair_line_data,
                                      key=lambda k: k['repair_type'])
        return repair_line_data

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or \
                not self.env.context.get('active_model') or \
                not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, \
                                this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        result = self.get_repair_line_detail(data.get('form'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_vehicle_history': result
        }
