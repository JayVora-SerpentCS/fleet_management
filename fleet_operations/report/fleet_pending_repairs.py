# See LICENSE file for full copyright and licensing details.
"""Fleet Pending Repairs Report."""

import base64
import io

from odoo import models

import xlwt


class FleetPendinRepair(models.AbstractModel):
    """Fleet pending repair."""

    _name = 'report.fleet_operations.fleet.pending.repairs.xls'
    _description = 'Fleet Pending Repair Report'

    def get_heading(self):
        """Method get heading."""
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

    def generate_pending_repairs_xlsx_report(self, res, fleet_pending):
        """Method generate pending repairs xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('fleet_pending')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 7500
        worksheet.col(2).width = 7500
        worksheet.col(3).width = 12500
        worksheet.col(4).width = 2500
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 7500
        worksheet.col(7).width = 5000
        worksheet.col(8).width = 2500
        font = xlwt.Font()
        # borders = xlwt.Borders()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: name 1; font: height 200')
        # format1 = xlwt.easyxf('font: bold 1; font: name 1;\
        #     font: height 200;')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'Fleet With Pending Repairs')
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
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
