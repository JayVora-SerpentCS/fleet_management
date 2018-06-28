# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import models


class NextServiceDate(models.AbstractModel):
    _name = 'report.fleet_operations.next.services.by.date.xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, next_service):
        worksheet = workbook.add_worksheet('next_service_by_date')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 8)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 17)
        worksheet.set_column(8, 8, 10)
        tot = workbook.add_format({'border': 2,
                                   'bold': True,
                                   'font_name': 'Arial',
                                   'font_size': '10'})
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
        worksheet.write(row, 2, 'Scheduled Maintenance By Date', merge_format)
        row += 3
        worksheet.write(row, 6, 'Date :', tot)
        worksheet.write(row, 7, time.strftime('%d-%B-%Y'), tot)
        row += 1
        worksheet.write(row, 0, 'NO.', format1)
        worksheet.write(row, 1, 'VEHICLE ID', format1)
        worksheet.write(row, 2, 'VIN NO.', format1)
        worksheet.write(row, 3, 'MAKE', format1)
        worksheet.write(row, 4, 'MODEL', format1)
        worksheet.write(row, 5, 'LAST SERVICE DATE', format1)
        worksheet.write(row, 6, 'NEXT SERVICE DATE', format1)
        worksheet.write(row, 7, 'REGISTRATION STATE', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in next_service:
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.vin_sn or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.f_brand_id and
                                obj.f_brand_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.model_id and
                                obj.model_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.last_service_date or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.next_service_date or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.vechical_location_id and
                                obj.vechical_location_id.name or '', border)
                line_col = 0
                line_row += 1
                counter += 1
                worksheet.write(line_row, line_col, '********', border)