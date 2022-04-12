# See LICENSE file for full copyright and licensing details.
"""Fleet Listing Report."""

import base64
import io

from odoo import models

import xlwt


class FleetListing(models.AbstractModel):
    """Fleet Listing Model."""

    _name = 'report.fleet_operations.fleet.summary.xls'
    _description = "Fleet Listing Report"

    def get_heading(self):
        """Report method get heading."""
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

    def generate_listing_xlsx_report(self, r, fleet_listing):
        """Generate Method to listing of report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('fleet_listing')
        worksheet.col(0).width = 7000
        worksheet.col(1).width = 10000
        worksheet.col(2).width = 7000
        worksheet.col(3).width = 8500
        worksheet.col(4).width = 7000
        worksheet.col(5).width = 8000
        worksheet.col(6).width = 8500
        worksheet.col(7).width = 7000
        worksheet.col(8).width = 7000
        worksheet.col(9).width = 7000
        worksheet.col(10).width = 8500
        worksheet.col(11).width = 8500
        worksheet.col(12).width = 8500

        font = xlwt.Font()
        # borders = xlwt.Borders()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        tit = xlwt.easyxf('font: name 1; font: height 220')
        # tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
                    pattern: pattern solid, fore_colour yellow;')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 1, 'Fleet Listing', format1)
        row = 1
        row += 3
        worksheet.write(row, 0, 'NO', format1)
        worksheet.write(row, 1, 'Vehicle ID', format1)
        worksheet.write(row, 2, 'VIN NO.', format1)
        worksheet.write(row, 3, 'ENGINE NO', format1)
        worksheet.write(row, 4, 'METER', format1)
        worksheet.write(row, 5, 'MAKE', format1)
        worksheet.write(row, 6, 'MODEL', format1)
        worksheet.write(row, 7, 'COLOR', format1)
        worksheet.write(row, 8, 'TYPE', format1)
        worksheet.write(row, 9, 'DRIVER NAME.', format1)
        worksheet.write(row, 10, 'DRIVER CONTACT', format1)
        line_row = row + 1

        line_col = 0
        counter = 1
        for obj in fleet_listing:
            worksheet.write(line_row, line_col, counter, border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.name or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.vin_sn or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.engine_no or '', border)
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
            worksheet.write(line_row, line_col, obj.driver_id and
                            obj.driver_id.name or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.driver_contact_no or '',
                            border)
            line_col = 0
            line_row += 1
            counter += 1
        worksheet.write(line_row, line_col, '********', border)
        row += 5
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodebytes(data)
        return res
