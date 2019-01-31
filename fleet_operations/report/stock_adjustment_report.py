# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class StockAdjustment(ReportXlsx):

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

    def generate_xlsx_report(self, workbook, data, stock):
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
#        worksheet.merge_range('C2:D2', 'Merged Cells', merge_format)
        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)

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
#        worksheet.write(row, 4, 'Rev. No. :', tot)
#        worksheet.write(row, 5, result.get('rev_no') or '', border)
#        worksheet.write(row, 6, 'Document No. :', tot)
#        worksheet.write(row, 7, result.get('doc_no') or '', border)
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


StockAdjustment('report.stock.adjustment.xls', 'qty.update.history')
