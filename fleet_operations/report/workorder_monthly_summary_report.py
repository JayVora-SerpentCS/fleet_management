# See LICENSE file for full copyright and licensing details.
"""WorkOrder monthly summary report."""

import base64
import io

from odoo import models
from odoo.exceptions import UserError

import xlwt


class WorkOrderMonthlyReportXlsx(models.AbstractModel):
    """Work Order Monthly Report Xlsx."""

    _name = 'report.fleet_operations.workorder.monthly.summary.xls'
    _description = 'Work Order Monthly Summary Report'

    def get_wo_mthly_smry(self, workorder_browse):
        """Method get wo monthly summary."""
        wo_summary_data = []
        wo_check_dict = {}
        no = 0
        if workorder_browse:
            for work_rec in workorder_browse:
                if work_rec.state and work_rec.state == 'done':
                    no += 1
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
                    if work_rec.parts_ids:
                        for parts_line in work_rec.parts_ids:
                            if work_rec.id in wo_check_dict.keys():
                                parts_data = {
                                    'no': -1,
                                    'location': '',
                                    'type': '',
                                    'wo': '',
                                    'identification': '',
                                    'vin': '',
                                    'plate_no': '',
                                    'work_performed': '',
                                    'part': parts_line.product_id and
                                    parts_line.product_id.default_code or '',
                                    'qty': parts_line.qty or 0.0,
                                    'uom': parts_line.product_uom and
                                    parts_line.product_uom.name or ''
                                }
                                wo_summary_data.append(parts_data)
                            else:
                                wo_check_dict[work_rec.id] = work_rec.id
                                parts_data = {
                                    'no': no,
                                    'location': work_rec.team_id and
                                    work_rec.team_id.name or '',
                                    'type': work_rec.main_type or '',
                                    'wo': work_rec.name or '',
                                    'identification': identification or '',
                                    'vin': work_rec.vehicle_id and
                                    work_rec.vehicle_id.vin_sn or '',
                                    'plate_no': work_rec.vehicle_id and
                                    work_rec.vehicle_id.license_plate or '',
                                    'work_performed': repair_line_data and
                                    repair_line_data[:-2] or '',
                                    'part': parts_line.product_id and
                                    parts_line.product_id.default_code or '',
                                    'qty': parts_line.qty or 0.0,
                                    'uom': parts_line.product_uom and
                                    parts_line.product_uom.name or ''
                                }
                                wo_summary_data.append(parts_data)
                    else:
                        parts_data = {
                            'no': no,
                            'location': work_rec.team_id and
                            work_rec.team_id.name or '',
                            'type': work_rec.main_type or '',
                            'wo': work_rec.name or '',
                            'identification': identification or '',
                            'vin': work_rec.vehicle_id and
                            work_rec.vehicle_id.vin_sn or '',
                            'plate_no': work_rec.vehicle_id and
                            work_rec.vehicle_id.license_plate or '',
                            'work_performed': repair_line_data and
                            repair_line_data[:-2] or '',
                            'vehicle_make': '',
                            'qty': '',
                            'uom': ''
                        }
                        wo_summary_data.append(parts_data)
        if not wo_summary_data:
            raise UserError("Warning! \n\
                No data Available for selected work order.")
        return wo_summary_data

    def generate_xlsx_report(self, workorder):
        """Generate XlSX Report."""

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('invoice')
        # worksheet.merge_range('B4:D4')
        worksheet.col(0).width = 3000
        worksheet.col(1).width = 7500
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 13000
        worksheet.col(5).width = 4000
        worksheet.col(6).width = 4000
        worksheet.col(7).width = 13000
        worksheet.col(8).width = 5000
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 5000
        worksheet.col(11).width = 7500
        worksheet.col(12).width = 7500
        worksheet.col(13).width = 7500
        worksheet.col(14).width = 7500
        worksheet.col(15).width = 7500

        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200; \
            align: horiz center')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200; \
            pattern: pattern solid, fore_colour yellow; align: horiz center')
        format2 = xlwt.easyxf('align: horiz center')
        format3 = xlwt.easyxf('align: horiz left')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 4,
                        'Vehicle Services Monthly Summary Report', border)
        row += 3

        worksheet.write(row, 0, 'Item No.', format1)
        worksheet.write(row, 1, 'Location', format1)
        worksheet.write(row, 2, 'Type', format1)
        worksheet.write(row, 3, 'Wo #', format1)
        worksheet.write(row, 4, 'Identification', format1)
        worksheet.write(row, 5, 'VIN', format1)
        worksheet.write(row, 6, 'Plate No.', format1)
        worksheet.write(row, 7, 'Work Performed', format1)
        row += 1
        counter = 1
        for line in self.get_wo_mthly_smry(workorder):
            if line.get('no') > 0:
                worksheet.write(row, 0, line.get('no'), format2)
                worksheet.write(row, 1, line.get('location'), format3)
                worksheet.write(row, 2, line.get('type'), format2)
                worksheet.write(row, 3, line.get('wo'), format2)
                worksheet.write(row, 4, line.get('identification'), format3)
                worksheet.write(row, 5, line.get('vin'), format2)
                worksheet.write(row, 6, line.get('plate_no'), format2)
                worksheet.write(row, 7, line.get('work_performed'), format3)
            if line.get('no') < 0:
                worksheet.write(row, 0, line.get('no'))
                worksheet.write(row, 1, line.get('location'))
                worksheet.write(row, 2, line.get('type'))
                worksheet.write(row, 3, line.get('wo'))
                worksheet.write(row, 4, line.get('identification'))
                worksheet.write(row, 5, line.get('vin'))
                worksheet.write(row, 6, line.get('plate_no'))
                worksheet.write(row, 7, line.get('work_performed'))
            row += 1
            counter += 1
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodebytes(data)
        return res
