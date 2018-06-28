# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models


class FleetWorkOrder(models.AbstractModel):
    _name = 'report.fleet_operations.workorder.summary.xls'
    _inherit = 'report.report_xlsx.abstract'

    def get_wo_status(self, status):
        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        else:
            wo_status = "New"
        return wo_status

    def get_wo_smry(self, workorder_browse):
        wo_summary_data = []
        wo_smry_dict = {}
        if workorder_browse:
            for work_rec in workorder_browse:
                if work_rec.state and work_rec.state == 'done':
                    identification = ''
                    repair_line_data = ''
                    if work_rec.vehicle_id:
                        identification += work_rec.vehicle_id.name
                        if work_rec.vehicle_id.f_brand_id:
                            identification += ' ' + \
                                work_rec.vehicle_id.f_brand_id.name
                        if work_rec.vehicle_id.model_id:
                            identification += ' ' + \
                                work_rec.vehicle_id.model_id.name
                    for repaire_line in work_rec.repair_line_ids:
                        if repaire_line.complete is True:
                            if repaire_line.repair_type_id and \
                                    repaire_line.repair_type_id.name:
                                repair_line_data += \
                                    repaire_line.repair_type_id.name + ', '

                    if wo_smry_dict.get(work_rec.team_id.id, False):
                        wo_data = {
                            'name': work_rec.name or '',
                            'identification': identification or '',
                            'vin': work_rec.vehicle_id and
                            work_rec.vehicle_id.vin_sn or '',
                            'date_open': work_rec.date_open or '',
                            'state': self.get_wo_status(work_rec.state),
                            'etic': work_rec.etic and
                            work_rec.date_complete or '',
                            'date_close': work_rec.date_close or '',
                            'work_performed': repair_line_data and
                            repair_line_data[:-2] or '',
                        }
                        wo_smry_dict[work_rec.team_id.id]['value'] += [wo_data]
                    else:
                        wo_data = \
                            {
                                'name': work_rec.name or '',
                                'identification': identification or '',
                                'vin': work_rec.vehicle_id and
                                work_rec.vehicle_id.vin_sn or '',
                                'date_open': work_rec.date_open or '',
                                'state': self.get_wo_status(work_rec.state),
                                'etic': work_rec.etic and
                                work_rec.date_complete or '',
                                'date_close': work_rec.date_close or '',
                                'work_performed': repair_line_data and
                                repair_line_data[:-2] or '',
                            }

                        wo_smry_dict[work_rec.team_id.id] = \
                            {
                                'team_id': work_rec.team_id and
                                work_rec.team_id.name or '',
                                'value': [wo_data]
                                }
        for team_id, workorder_data in wo_smry_dict.items():
            wo_summary_data.append(workorder_data)
        return wo_summary_data

    def generate_xlsx_report(self, workbook, data, product):
        worksheet = workbook.add_worksheet('workorder_summary')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 50)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 8)
        worksheet.set_column(7, 7, 12)
        worksheet.set_column(8, 8, 20)
        worksheet.set_column(9, 9, 50)
        worksheet.set_column(10, 10, 15)

        tot = workbook.add_format({'border': 2,
                                   'font_name': 'Arial',
                                   'font_size': '12'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'Work Order Summary', tot)
        row += 4
        worksheet.write(row, 0, 'NO.', format1)
        worksheet.write(row, 1, 'WO No.', format1)
        worksheet.write(row, 2, 'Identification', format1)
        worksheet.write(row, 3, 'VIN', format1)
        worksheet.write(row, 4, 'Actual Date Issued', format1)
        worksheet.write(row, 5, 'Status', format1)
        worksheet.write(row, 6, 'ETIC', format1)
        worksheet.write(row, 7, 'WO Date Closed', format1)
        worksheet.write(row, 8, 'Workshop', format1)
        worksheet.write(row, 9, 'Work Performed', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in self.get_wo_smry(product):
            for line in obj.get('value'):
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('name') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('identification') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('vin') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('date_open') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('state') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('etic') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('date_close') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('team_id')or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('work_performed') or '', border)
                line_col = 0
                line_row += 1
                counter += 1
            worksheet.write(line_row, line_col, '********', border)