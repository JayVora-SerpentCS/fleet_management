# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import base64
from odoo import models


class FleetPendinRepair(models.AbstractModel):
    _name = 'report.fleet_operations.fleet.pending.repairs.xls'
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
        worksheet = workbook.add_worksheet('fleet_pending')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 25)
        worksheet.set_column(4, 4, 5)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 5)

#        result = self.get_heading()
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
        worksheet.merge_range('C3:D3', 'Merged Cells', merge_format)
#        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)

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
        worksheet.write(row, 2, 'Fleet With Pending Repairs', merge_format)
        row += 2
        for obj in fleet_pending:
            if obj.pending_repair_type_ids:
                row += 3
                worksheet.write(row, 0, 'Vehicle Information :')
                row += 2
                worksheet.write(row, 2, 'Kilometer :', tot)
                worksheet.write(row, 3, obj.odometer or '', border)
                row += 1
                worksheet.write(row, 2, 'Vehicle ID :', tot)
                worksheet.write(row, 3, obj.name or '', border)
                row += 1
                worksheet.write(row, 2, 'Type :', tot)
                worksheet.write(row, 3, obj.vechical_type_id and
                                obj.vechical_type_id.name or '', border)
                row += 1
                worksheet.write(row, 2, 'VIN :', tot)
                worksheet.write(row, 3, obj.vin_sn or '', border)
                row += 1
                worksheet.write(row, 2, 'Color :', tot)
                worksheet.write(row, 3, obj.vehical_color_id and
                                obj.vehical_color_id.name or '', border)
                row += 1
                worksheet.write(row, 2, 'Driver :', tot)
                worksheet.write(row, 3, obj.driver_id and
                                obj.driver_id.name or '', border)
                row += 1
                worksheet.write(row, 2, 'Driver Contact :', tot)
                worksheet.write(row, 3, obj.driver_contact_no or '', border)
                row += 4
                worksheet.write(row, 0, 'Repair Types :')
                row += 1
                worksheet.write(row, 1, 'No. :', tot)
                worksheet.write(row, 2, 'Ref. WO# :', tot)
                worksheet.write(row, 3, 'Repair Type :', tot)
                worksheet.write(row, 5, 'Category :', tot)
                worksheet.write(row, 6, 'Actual Date Issued :', tot)
                row += 1
                counter = 1
                for line in obj.pending_repair_type_ids:
                    worksheet.write(row, 1, counter, border)
                    worksheet.write(row, 2, line.name or '', border)
                    worksheet.write(row, 3, line.repair_type_id and
                                    line.repair_type_id.name or '', border)
                    worksheet.write(row, 5, line.categ_id and
                                    line.categ_id.name or '', border)
                    worksheet.write(row, 6, line.issue_date or '', border)
                    row += 1
                    counter += 1
                row += 3
                worksheet.write(row, 0, '**************************')
                worksheet.write(row, 1, '**************************')
                worksheet.write(row, 2, '**************************')
                worksheet.write(row, 3, '**************************')
                worksheet.write(row, 4, '**************************')
                worksheet.write(row, 5, '**************************')
                worksheet.write(row, 6, '**************************')
                worksheet.write(row, 7, '**************************')
                row += 1
                worksheet.write(row, 0, '**************************')
                worksheet.write(row, 1, '**************************')
                worksheet.write(row, 2, '**************************')
                worksheet.write(row, 3, '**************************')
                worksheet.write(row, 4, '**************************')
                worksheet.write(row, 5, '**************************')
                worksheet.write(row, 6, '**************************')
                worksheet.write(row, 7, '**************************')
