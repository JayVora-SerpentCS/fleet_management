# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import base64
from odoo import models


class FleetPending(models.AbstractModel):
    _name = 'report.fleet_operations.fleet.pending.xls'
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

    def generate_xlsx_report(self, workbook, data, fleet_pending):
        worksheet = workbook.add_worksheet('fleet_pending_summary')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 8)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 8)
        worksheet.set_column(5, 5, 8)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(10, 10, 15)
        worksheet.set_column(11, 11, 20)
        worksheet.set_column(12, 12, 10)
        worksheet.set_column(13, 13, 5)
        worksheet.set_column(14, 14, 5)
        worksheet.set_column(15, 15, 5)

#        result = self.get_heading()
        tit = workbook.add_format({'border': 2,
                                   'font_name': 'Arial',
                                   'font_size': '12'})
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
        row = 0
        row += 1
#        if file_name:
#            worksheet.insert_image(row, 0, '/tmp/logo.png')
#        worksheet.write(row, 2, result.get('name') or '', border)
#        worksheet.write(row, 5, 'Rev. No. :', tot)
#        worksheet.write(row, 6, result.get('rev_no') or '', border)
#        worksheet.write(row, 7, 'Document No. :', tot)
#        worksheet.write(row, 8, result.get('doc_no') or '', border)
        row += 1
        worksheet.write(row, 2, 'Fleet Repairs Pending', tit)
        row += 2
        worksheet.write(row, 0, 'No', format1)
        worksheet.write(row, 1, 'Vehicle ID', format1)
        worksheet.write(row, 2, 'VIN NO.', format1)
        worksheet.write(row, 3, 'ENGINE NO', format1)
        worksheet.write(row, 4, 'METER', format1)
        worksheet.write(row, 5, 'MAKE', format1)
        worksheet.write(row, 6, 'MODEL', format1)
        worksheet.write(row, 7, 'COLOR', format1)
        worksheet.write(row, 8, 'TYPE', format1)
        worksheet.write(row, 9, 'CONTACT NO', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in fleet_pending:
            if obj.pending_repair_type_ids:
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
                worksheet.write(line_row, line_col, obj.vehical_color_id and
                                obj.vehical_color_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.vechical_type_id and
                                obj.vechical_type_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.driver_contact_no or '', border)
                line_col = 0
                line_row += 1
                counter += 1
                worksheet.write(line_row, line_col, '********', border)
                