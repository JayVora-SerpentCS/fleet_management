# See LICENSE file for full copyright and licensing details.
"""Fleet Pending Repairs Report."""

import base64
import io
from odoo.tools import format_date
from odoo import models

import xlwt


class FleetPendingRepair(models.AbstractModel):
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
        worksheet.col(0).width = 6000
        worksheet.col(1).width = 6000
        worksheet.col(2).width = 7500
        worksheet.col(3).width = 12500
        worksheet.col(4).width = 5500
        worksheet.col(5).width = 6000
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
        style1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200', num_format_str='DD/MM/YYYY')
        # border = xlwt.easyxf('font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
                    pattern: pattern solid, fore_colour yellow;')

        row = 0
        row += 1
        worksheet.write(row, 2, 'Fleet With Pending Repairs', format1)
        row += 2
        for obj in fleet_pending:
            if obj.pending_repair_type_ids:
                row += 3
                worksheet.write(row, 0, 'Vehicle Information :',format1)
                row += 2
                worksheet.write(row, 2, 'Kilometer :', format1)
                worksheet.write(row, 3, obj.odometer or '', tot)
                row += 1
                worksheet.write(row, 2, 'Vehicle ID :', format1)
                worksheet.write(row, 3, obj.name or '', tot)
                row += 1
                worksheet.write(row, 2, 'Type :', format1)
                worksheet.write(row, 3, obj.vechical_type_id and
                                obj.vechical_type_id.name or '', tot)
                row += 1
                worksheet.write(row, 2, 'VIN :', format1)
                worksheet.write(row, 3, obj.vin_sn or '', tot)
                row += 1
                worksheet.write(row, 2, 'Color :', format1)
                worksheet.write(row, 3, obj.vehical_color_id and
                                obj.vehical_color_id.name or '', tot)
                row += 1
                worksheet.write(row, 2, 'Driver :', format1)
                worksheet.write(row, 3, obj.driver_id and
                                obj.driver_id.name or '', tot)
                row += 1
                worksheet.write(row, 2, 'Driver Contact :', format1)
                worksheet.write(row, 3, obj.driver_contact_no or '', tot)
                row += 4
                worksheet.write(row, 0, 'Repair Types :', format1)
                row += 2
                worksheet.write(row, 1, 'No. :', format1)
                worksheet.write(row, 2, 'Ref. WO# :', format1)
                worksheet.write(row, 3, 'Repair Type :', format1)
                worksheet.write(row, 4, 'Category :', format1)
                worksheet.write(row, 5, 'Actual Date Issued :', format1)
                row += 1
                counter = 1
                for line in obj.pending_repair_type_ids:
                    worksheet.write(row, 1, counter, tot)
                    worksheet.write(row, 2, line.name or '', tot)
                    worksheet.write(row, 3, line.repair_type_id and
                                    line.repair_type_id.name or '', tot)
                    worksheet.write(row, 4, line.categ_id and
                                    line.categ_id.name or '', tot)

                    date = ''
                    if line.issue_date:
                        date = format_date(
                            self.env, line.issue_date, self._context.get('lang'),
                            date_format=False
                        )
                    worksheet.write(row, 5, date or '', style1)
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
                row += 1
                worksheet.write(row, 0, '**************************')
                worksheet.write(row, 1, '**************************')
                worksheet.write(row, 2, '**************************')
                worksheet.write(row, 3, '**************************')
                worksheet.write(row, 4, '**************************')
                worksheet.write(row, 5, '**************************')
                worksheet.write(row, 6, '**************************')
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodebytes(data)
        return res
