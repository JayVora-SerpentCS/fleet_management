# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models


class FleetRentalVehicleHistory(models.AbstractModel):
    _name = 'report.fleet_rent.fleet.rental.vehicle.history.xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, fleet_rental):
        worksheet = workbook.add_worksheet('fleet_rental')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 5)
        worksheet.set_column(4, 4, 20)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(10, 10, 15)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 20)
        worksheet.set_column(13, 13, 20)
        worksheet.set_column(14, 14, 5)

        tot = workbook.add_format({'border': 2,
                                   'font_name': 'Arial',
                                   'font_size': '12'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        merge_format = workbook.add_format({'border': 2, 'align': 'center'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)

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
