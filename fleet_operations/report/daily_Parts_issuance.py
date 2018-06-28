# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
import base64
from odoo import models


class DailyPartIssuance(models.AbstractModel):
    _name = 'report.fleet_operations.daily.parts.issuance.xls'
    _inherit = 'report.report_xlsx.abstract'

    def get_heading(self):
        head_title = {'name': '',
                      'rev_no': '',
                      'doc_no': '',
                      }
        head_object = self.env['report.heading']
        head_ids = head_object.search([], order='id')
        if head_ids:
            head_rec = head_ids[0]
            if head_rec:
                head_title['name'] = head_rec.name or ''
                head_title['rev_no'] = head_rec.revision_no or ''
                head_title['doc_no'] = head_rec.document_no or ''
                head_title['image'] = head_rec.image or ''
        return head_title

    def generate_xlsx_report(self, workbook, data, parts_data):
        worksheet = workbook.add_worksheet('daily_parts_issuance')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 8)
        worksheet.set_column(7, 7, 12)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 15)
        worksheet.set_column(10, 10, 15)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 20)
        worksheet.set_column(13, 13, 5)
        worksheet.set_column(14, 14, 5)
        worksheet.set_column(15, 15, 5)

#        result = self.get_heading()
        bold = workbook.add_format({'bold': True,
                                    'font_name': 'Arial',
                                    'font_size': '10'})
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
#        worksheet.merge_range('C2:E2', 'Merged Cells', merge_format)
        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)

#        file_name = result.get('image', False)
#        if file_name:
#            file1 = open('/tmp/' + 'logo.png', 'wb')
#            file_data = base64.decodestring(file_name)
#            file1.write(file_data)
#            file1.close()

        row = 1
#        if file_name:
#            worksheet.insert_image(row, 0, '/tmp/logo.png')
#        worksheet.write(row, 2, result.get('name') or '', border)
#        worksheet.write(row, 5, 'Rev. No. :', tot)
#        worksheet.write(row, 6, result.get('rev_no') or '', border)
#        worksheet.write(row, 7, 'Document No. :', tot)
#        worksheet.write(row, 8, result.get('doc_no') or '', border)
        row += 1
        worksheet.write(row, 2, 'DAILY PARTS ISSUANCE', tot)
        row += 4
        worksheet.write(row, 9, 'DATE ISSUED :', bold)
        worksheet.write(row, 10, time.strftime('%d-%B-%Y'))
        row += 1
        worksheet.write(row, 0, 'NO.', format1)
        worksheet.write(row, 1, 'WO NO.', format1)
        worksheet.write(row, 2, 'VEHICLE ID', format1)
        worksheet.write(row, 3, 'PART NO.', format1)
        worksheet.write(row, 4, 'PART NAME', format1)
        worksheet.write(row, 5, 'VEHICLE MAKE', format1)
        worksheet.write(row, 6, 'USED', format1)
        worksheet.write(row, 7, 'UNIT TYPE', format1)
        worksheet.write(row, 8, 'OLD PART RETURND', format1)
        worksheet.write(row, 9, 'ISSUED BY', format1)
        worksheet.write(row, 10, 'REMARKS', format1)

        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in parts_data:
            for line in obj.parts_ids:
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.fleet_service_id and
                                line.fleet_service_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.fleet_service_id and
                                line.fleet_service_id.vehicle_id and
                                line.fleet_service_id.vehicle_id.name or '',
                                border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.product_id and
                                line.product_id.default_code or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.product_id and
                                line.product_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.vehicle_make_id and
                                line.vehicle_make_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.qty or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.product_uom and
                                line.product_uom.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.old_part_return or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.issued_by and
                                line.issued_by.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.fleet_service_id and
                                line.fleet_service_id.note or '', border)
                line_col = 0
                line_row += 1
                counter += 1
                worksheet.write(line_row, line_col, '********', border)
