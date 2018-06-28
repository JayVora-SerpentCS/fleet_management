# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models


class FleetWaitingColletion(models.AbstractModel):
    _name = 'report.fleet_operations.fleet.wait.collection.xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, fleet_waiting):
        worksheet = workbook.add_worksheet('fleet_waiting_collection')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 8)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 8)
        worksheet.set_column(5, 5, 8)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 17)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 15)
        worksheet.set_column(10, 10, 15)
        worksheet.set_column(11, 11, 20)
        worksheet.set_column(12, 12, 10)
        worksheet.set_column(13, 13, 5)
        worksheet.set_column(14, 14, 5)
        worksheet.set_column(15, 15, 5)
        
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        merge_format = workbook.add_format({'border': 2, 'align': 'center'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
        worksheet.merge_range('C3:E3', 'Merged Cells', merge_format)
        row = 0
        row += 1

        row += 1
        worksheet.write(row, 2, 'Fleet In Complete Stage', merge_format)
        row += 4
        worksheet.write(row, 0, 'No', format1)
        worksheet.write(row, 1, 'Vehicle ID', format1)
        worksheet.write(row, 2, 'VIN NO.', format1)
        worksheet.write(row, 3, 'ENGINE NO', format1)
        worksheet.write(row, 4, 'METER', format1)
        worksheet.write(row, 5, 'MAKE', format1)
        worksheet.write(row, 6, 'MODEL', format1)
        worksheet.write(row, 7, 'REGISTRATION STATE', format1)
        worksheet.write(row, 8, 'DRIVER', format1)
        worksheet.write(row, 9, 'DRIVER CONTACT NO', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in fleet_waiting:
            if obj.state == 'complete':
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.vin_sn or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.engine_no or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.odometer or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.f_brand_id and
                                obj.f_brand_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.model_id and
                                obj.model_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.vechical_location_id and
                                obj.vechical_location_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.driver_id and
                                obj.driver_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.driver_contact_no or '', border)
                line_col = 0
                line_row += 1
                counter += 1
                worksheet.write(line_row, line_col, '********', border)
                