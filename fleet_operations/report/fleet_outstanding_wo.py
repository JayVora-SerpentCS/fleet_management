# See LICENSE file for full copyright and licensing details.
"""Fleet Outstanding Wo Report."""


import base64
import io

from odoo import models

import xlwt


class FleetOutstandingWO(models.AbstractModel):
    """Fleet Outstanding Wo."""

    _name = 'report.fleet_operations.outstanding.wo.xls'
    _description = 'Fleet Outstanding Workorder Report'

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

    def get_wo_status(self, status):
        """Method get wo status."""
        wo_status = ""

        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        else:
            wo_status = "New"
        return wo_status

    def get_work_incomplete(self, workorder_id):
        """Method get work incomplate."""
        repair_type = ""
        if workorder_id:
            for repair_line in workorder_id.repair_line_ids:
                if not repair_line.complete:
                    repair_type += repair_line.repair_type_id.name + ","
        return repair_type[:-1]

    def generate_xlsx_report(self, product):
        """Generate xlsx report format."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('outstanding_wo')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 7500
        worksheet.col(2).width = 12000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 6000
        worksheet.col(6).width = 4000
        worksheet.col(7).width = 6000
        worksheet.col(8).width = 10000
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 7500
        worksheet.col(11).width = 5000
        worksheet.col(12).width = 10000
        worksheet.col(13).width = 2500
        worksheet.col(14).width = 2500
        worksheet.col(15).width = 2500

        font = xlwt.Font()
        # borders = xlwt.Borders()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        # tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'Outstanding Work Order', border)
        row += 2
        worksheet.write(row, 0, 'NO.', format1)
        worksheet.write(row, 1, 'WO NO.', format1)
        worksheet.write(row, 2, 'VEHICLE ID', format1)
        worksheet.write(row, 3, 'VIN', format1)
        worksheet.write(row, 4, 'Make', format1)
        worksheet.write(row, 5, 'Model', format1)
        worksheet.write(row, 6, 'Status', format1)
        worksheet.write(row, 7, 'ETIC', format1)
        worksheet.write(row, 8, 'On Going Job', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in product:
            worksheet.write(line_row, line_col, counter)
            line_col += 1
            worksheet.write(line_row, line_col,
                            obj.name or '')
            line_col += 1
            worksheet.write(line_row, line_col,
                            obj.vehicle_id and
                            obj.vehicle_id.name or '')
            line_col += 1
            worksheet.write(line_row, line_col,
                            obj.vehicle_id and
                            obj.vehicle_id.vin_sn or '')
            line_col += 1
            worksheet.write(line_row, line_col,
                            obj.vehicle_id and
                            obj.vehicle_id.f_brand_id and
                            obj.vehicle_id.f_brand_id.name or '')
            line_col += 1
            worksheet.write(line_row, line_col,
                            obj.vehicle_id and
                            obj.vehicle_id.model_id and
                            obj.vehicle_id.model_id.name or '')
            line_col += 1
            worksheet.write(line_row, line_col,
                            self.get_wo_status(obj.state) or '')
            line_col += 1
            worksheet.write(line_row, line_col,
                            obj.etic and
                            obj.date_complete or '')
            line_col += 1
            worksheet.write(line_row, line_col,
                            self.get_work_incomplete(obj) or '')
            line_col = 0
            line_row += 1
            counter += 1
        worksheet.write(line_row, line_col, '********')
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
