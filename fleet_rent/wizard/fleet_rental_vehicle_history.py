# See LICENSE file for full copyright and licensing details.
"""Fleet Rental Vehicle History Wizard."""

import base64
import io

from odoo import fields, models

import xlwt


class FleetRentalVehicleHistory(models.TransientModel):
    """Fleet Rental Vehicle History."""

    _name = 'rental.fleet.history'
    _description = 'Rental Fleet History Report'

    name = fields.Char(string="File Name")
    file = fields.Binary(string="File", readonly=True)

    def rental_vehicle_history(self):
        """Method rental vehicle history."""
        docids = self.env.context.get('active_ids')
        fleet_rental = self.env[self.env.context.get(
            'active_model')].browse(docids) or False
        file = self.generate_xlsx_report(fleet_rental)
        self.write({'name': 'Vehicle Rental History.xls',
                    'file': file})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'rental.fleet.history',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id
        }

    def generate_xlsx_report(self, fleet_rental):
        """Method to generate xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('fleet_rental')
        worksheet.col(0).width = 7000
        worksheet.col(1).width = 7500
        worksheet.col(2).width = 15000
        worksheet.col(3).width = 2500
        worksheet.col(4).width = 10000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 5000
        worksheet.col(7).width = 7500
        worksheet.col(8).width = 7500
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 7500
        worksheet.col(11).width = 5000
        worksheet.col(12).width = 10000
        worksheet.col(13).width = 10000
        worksheet.col(14).width = 2500

        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 300')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'Fleet Rental Vehicle History', tot)
        row = 1
        row += 3
        worksheet.write(row, 0, 'NO', format1)
        worksheet.write(row, 1, 'Date', format1)
        worksheet.write(row, 2, 'Rental Vehicle Name', format1)
        worksheet.write(row, 3, 'Code', format1)
        worksheet.write(row, 4, 'Vehicle', format1)
        worksheet.write(row, 5, 'Odometer', format1)
        worksheet.write(row, 6, 'Tenant', format1)
        worksheet.write(row, 7, 'Start Date', format1)
        worksheet.write(row, 8, 'Expiration Date', format1)
        worksheet.write(row, 9, 'Rent Type', format1)
        worksheet.write(row, 10, 'Rental vehicle Rent', format1)
        worksheet.write(row, 11, 'Total Rent', format1)
        worksheet.write(row, 12, 'Rent Cancel Date', format1)
        worksheet.write(row, 13, 'Rent Cancel By', format1)
        worksheet.write(row, 14, 'Status', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in fleet_rental:
            worksheet.write(line_row, line_col, counter, border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.date or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.name or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.code or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.vehicle_id and
                            obj.vehicle_id.name or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.odometer or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.tenant_id and
                            obj.tenant_id.name or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.date_start or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.date or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.rent_type_id and
                            obj.rent_type_id.name or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.rent or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.total_rent or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.date_cancel or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.cancel_by_id and
                            obj.cancel_by_id.name or '', border)
            line_col += 1
            worksheet.write(line_row, line_col, obj.state or '', border)
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
        res = base64.encodestring(data)
        return res
