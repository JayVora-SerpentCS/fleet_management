# See LICENSE file for full copyright and licensing details.
"""General parts listing Report."""

import base64
import io

from odoo import models

import xlwt


class GeneralPartsListingXlsx(models.AbstractModel):
    """General Parts Listing Xlsxl."""

    _name = 'report.fleet_operations.general.parts.listing.xls'
    _description = 'Genral Parts Listing Reports'

    def generate_xlsx_report(self, parts):
        """Method to generate xlsx report."""
        # add the worksheet
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('product')
        worksheet.col(0).width = 2500
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 4500
        worksheet.col(5).width = 6000
        worksheet.col(6).width = 5000
        worksheet.col(7).width = 7500
        worksheet.col(8).width = 5000
        worksheet.col(9).width = 4500
        worksheet.col(10).width = 4500
        worksheet.col(11).width = 9000
        worksheet.col(12).width = 7500
        worksheet.col(13).width = 6000
        worksheet.col(14).width = 6000
        worksheet.col(15).width = 6000

        font = xlwt.Font()
        # borders = xlwt.Borders()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        size = xlwt.easyxf('font: bold 1; font: name 1; font: height 220')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid')

        row = 0
        for pr in parts:
            row += 1
            row += 1
            worksheet.write(row, 3, ' General Parts Listing ', size)
            row += 3
            worksheet.write(row, 0, 'No.', format1)
            worksheet.write(row, 1, 'Part No:', format1)
            worksheet.write(row, 2, 'Part Name', format1)
            worksheet.write(row, 3, 'Vehicle Make', format1)
            worksheet.write(row, 4, 'Location ', format1)
            worksheet.write(row, 5, 'Unit Type', format1)
            worksheet.write(row, 6, 'Qty ', format1)
            worksheet.write(row, 7, 'Incomming ', format1)
            worksheet.write(row, 8, 'Outgoing', format1)
            worksheet.write(row, 9, 'Ending Balance', format1)
            worksheet.write(row, 10, 'Reorder point', format1)
            worksheet.write(row, 11, 'Reorder Qty', format1)
            row += 2
            counter = 1
            for line in pr:
                worksheet.write(row, 0, counter, size)
                worksheet.write(row, 1, line.default_code or "")
                worksheet.write(row, 2, line.name or "")
                worksheet.write(row, 3, line.vehicle_make_id and
                                line.vehicle_make_id.name or "")
                worksheet.write(row, 4, 'Location')
                worksheet.write(row, 5, line.uom_id and line.uom_id.name or "")
                worksheet.write(row, 6, line.qty_available or 0.0)
                worksheet.write(row, 7, line.incoming_qty or 0.0)
                worksheet.write(row, 8, line.outgoing_qty or 0.0)
                worksheet.write(row, 9, line.virtual_available or 0.0)
                worksheet.write(row, 10, line.re_order_point or 0.0)
                worksheet.write(row, 11, line.re_order_qty or 0.0)
                counter += 1
        row += 8
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
