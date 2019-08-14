# See LICENSE file for full copyright and licensing details.
"""Next services Date."""

import base64
import io
import time

from odoo import models

import xlwt


class NextServiceDate(models.AbstractModel):
    """Next service date."""

    _name = 'report.fleet_operations.next.services.by.date.xls'
    _description = 'Next Service by Date'

    def generate_service_date_xlsx_report(self, res, next_service):
        """Metho to generate service date xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('next_service_by_date')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 12500
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 7500
        worksheet.col(5).width = 7500
        worksheet.col(6).width = 7500
        worksheet.col(7).width = 8500
        worksheet.col(8).width = 5000
        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'Scheduled Maintenance By Date')
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
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
