# See LICENSE file for full copyright and licensing details.
"""Fleet Waiting Collection."""

import base64
import io

from odoo import models

import xlwt


class FleetWaitingCollection(models.AbstractModel):
    """Fleet waiting collection."""

    _name = 'report.fleet_operations.fleet.wait.collection.xls'
    _description = 'Fleet Waiting Collection Report'

    def generate_complete_stage_xlsx_report(self, res, fleet_waiting):
        """Method generate complete stage xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('fleet_waiting_collection')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 12500
        worksheet.col(2).width = 7000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 7500
        worksheet.col(7).width = 8000
        worksheet.col(8).width = 7000
        worksheet.col(9).width = 7500
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
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
                    pattern: pattern solid, fore_colour yellow;')

        row = 0
        row += 1

        row += 1
        worksheet.write(row, 2, 'Fleet In Complete Stage', format1)
        row += 4
        worksheet.write(row, 0, 'No', format1)
        worksheet.write(row, 1, 'Vehicle ID', format1)
        worksheet.write(row, 2, 'VIN NO.', format1)
        worksheet.write(row, 3, 'ENGINE NO', format1)
        worksheet.write(row, 4, 'METER', format1)
        worksheet.write(row, 5, 'MAKE', format1)
        worksheet.write(row, 6, 'MODEL', format1)
        # worksheet.write(row, 7, 'REGISTRATION STATE', format1)
        worksheet.write(row, 7, 'DRIVER', format1)
        worksheet.write(row, 8, 'DRIVER CONTACT NO', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in fleet_waiting:
            if obj.state == 'complete':
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
                # line_col += 1
                # worksheet.write(line_row, line_col,
                #                 obj.vechical_location_id and
                #                 obj.vechical_location_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.driver_id and
                                obj.driver_id.name or '', border)
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
        res = base64.encodebytes(data)
        return res
