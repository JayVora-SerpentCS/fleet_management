# See LICENSE file for full copyright and licensing details.
"""Stock Adjustment Report."""

from odoo import models


class StockAdjustment(models.AbstractModel):
    """Stock adjustment."""

    _name = 'report.fleet_operations.stock.adjustment.xls'
    _description = 'Stock Adjustment Report'

    def generate_xlsx_report(self, workbook, data, stock):
        """Method to generate xlsx report."""
        worksheet = workbook.add_worksheet('stock_adjustment')
        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 8)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 10)
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
        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'STOCK ADJUSTMENT', tot)
        row += 3
        worksheet.write(row, 0, 'No.', format1)
        worksheet.write(row, 1, 'Date Adjusted', format1)
        worksheet.write(row, 2, 'Part No', format1)
        worksheet.write(row, 3, 'Part Name', format1)
        worksheet.write(row, 4, 'Vehicle Make', format1)
        worksheet.write(row, 5, 'Qty. Adjusted', format1)
        worksheet.write(row, 6, 'Adjusted By.', format1)
        worksheet.write(row, 7, 'Remarks', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in stock:
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.date or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.product_id and
                                obj.product_id.default_code or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.product_id and
                                obj.product_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.product_id and
                                obj.product_id.vehicle_make_id and
                                obj.product_id.vehicle_make_id.name or '',
                                border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.qty_adjust or '',
                                border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.user_id and
                                obj.user_id.name or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, obj.reason or '', border)
                line_col = 0
                line_row += 1
                counter += 1
                worksheet.write(line_row, line_col, '********', border)
