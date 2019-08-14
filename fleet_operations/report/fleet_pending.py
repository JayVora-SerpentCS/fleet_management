# See LICENSE file for full copyright and licensing details.
"""Fleet Pending Report."""


import base64
import io

from odoo import models

import xlwt


class FleetPending(models.AbstractModel):
    """Fleet Pending Report."""

    _name = 'report.fleet_operations.fleet.pending.xls'
    _description = 'Fleet Pending Report'

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

    def generate_pending_summary_xlsx_report(self, res, fleet_pending):
        """Method generate pending summary xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('fleet_pending_summary')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 10000
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 4000
        worksheet.col(5).width = 4000
        worksheet.col(6).width = 7500
        worksheet.col(7).width = 5000
        worksheet.col(8).width = 5000
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 7500
        worksheet.col(11).width = 10000
        worksheet.col(12).width = 5000
        worksheet.col(13).width = 2500
        worksheet.col(14).width = 2500
        worksheet.col(15).width = 2500
        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        tit = xlwt.easyxf('font: name 1; font: height 220')
        # tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid')

        row = 0
        row += 1
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
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
