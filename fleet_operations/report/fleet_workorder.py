# See LICENSE file for full copyright and licensing details.
"""Fleet Workorder Report."""

import base64
import io

from odoo import models

import xlwt


class FleetWorkOrder(models.AbstractModel):
    """Fleet Work Order."""

    _name = 'report.fleet_operations.workorder.summary.xls'
    _description = 'Fleet WorkOrder Reports'

    def get_wo_status(self, status):
        """Method get wo status."""
        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        else:
            wo_status = "New"
        return wo_status

    def get_wo_smry(self, workorder_browse):
        """Method get wo smry."""
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
                                'value': [wo_data]}
        for team_id, workorder_data in wo_smry_dict.items():
            wo_summary_data.append(workorder_data)
        return wo_summary_data

    def generate_xlsx_report(self, product):
        """Method to generate xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('workorder_summary')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 7500
        worksheet.col(2).width = 20000
        worksheet.col(3).width = 7500
        worksheet.col(4).width = 7500
        worksheet.col(5).width = 6000
        worksheet.col(6).width = 4000
        worksheet.col(7).width = 6000
        worksheet.col(8).width = 10000
        worksheet.col(9).width = 20000
        worksheet.col(10).width = 7500

        font = xlwt.Font()
        # borders = xlwt.Borders()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        # tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'Work Order Summary', border)
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
                worksheet.write(line_row, line_col, counter)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('name') or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('identification') or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('vin') or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('date_open') or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('state') or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('etic') or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('date_close') or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('team_id')or '')
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('work_performed') or '')
                line_col = 0
                line_row += 1
                counter += 1
            worksheet.write(line_row, line_col, '********')
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
