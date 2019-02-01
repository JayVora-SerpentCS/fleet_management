# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class GeneralPartsListingXlsx(ReportXlsx):
    def get_heading(self):
        head_title = {
            'name': '',
            'rev_no': '',
            'doc_no': '',
            'image': ''
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

    def generate_xlsx_report(self, workbook, data, parts):
        # add the worksheet
        worksheet = workbook.add_worksheet('product')
        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 10)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 9)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 9)
        worksheet.set_column(10, 10, 9)
        worksheet.set_column(11, 11, 18)
        worksheet.set_column(12, 12, 15)
        worksheet.set_column(13, 13, 12)
        worksheet.set_column(14, 14, 12)
        worksheet.set_column(15, 15, 12)
        bold = workbook.add_format({'bold': True,
                                    'font_name': 'Arial',
                                    'font_size': '10'})
        tot = workbook.add_format({'border': 2,
                                   'bold': True,
                                   'font_name': 'Arial',
                                   'font_size': '10'})
        tot.set_bg_color('gray')
#        res = self.get_heading()
#        file_name = res.get('image', False)
#        if file_name:
#            file1 = open('/tmp/' + 'logo.png', 'wb')
#            file_data = base64.decodestring(file_name)
#            file1.write(file_data)
#            file1.close()
        row = 0
        for pr in parts:
            row += 1
#            if file_name:
#                worksheet.insert_image(row, 0, '/tmp/logo.png')
#            worksheet.write(row, 3, res['name'], bold)
#            worksheet.write(row, 5, 'Rev No.', bold)
#            worksheet.write(row, 6, res['rev_no'])
#            worksheet.write(row, 7, 'Document No. :', bold)
#            worksheet.write(row, 8, res['doc_no'])
            row += 1
            worksheet.write(row, 3, ' General Parts Listing ', bold)
            row += 3
            worksheet.write(row, 0, 'No.', tot)
            worksheet.write(row, 1, 'Part No:', tot)
            worksheet.write(row, 2, 'Part Name', tot)
            worksheet.write(row, 3, 'Vehicle Make', tot)
            worksheet.write(row, 4, 'Location ', tot)
            worksheet.write(row, 5, 'Unit Type', tot)
            worksheet.write(row, 6, 'Qty ', tot)
            worksheet.write(row, 7, 'Incomming ', tot)
            worksheet.write(row, 8, 'Outgoing', tot)
            worksheet.write(row, 9, 'Ending Balance', tot)
            worksheet.write(row, 10, 'Reorder point', tot)
            worksheet.write(row, 11, 'Reorder Qty', tot)
            row += 2
            counter = 1
            for line in pr:
                worksheet.write(row, 0, counter, bold)
                worksheet.write(row, 1, line.default_code or "")
                worksheet.write(row, 2, line.name or "")
                worksheet.write(row, 3, line.vehicle_make_id and
                                line.vehicle_make_id.name or "")
                worksheet.write(row, 4, 'Location')
                worksheet.write(row, 5, line.uom_id and line.uom_id.name or "")
                worksheet.write(row, 6, line.qty_available or 0.0)
                worksheet.write(row, 7, line.incoming_qty or 0.0)
                worksheet.write(row, 8, line.outgoing_qty or 0.0)
                worksheet.write(row, 9, line.virtual_available or 0.0)
                worksheet.write(row, 10, line.re_order_point or 0.0)
                worksheet.write(row, 11, line.re_order_qty or 0.0)
                counter += 1
        row += 8


GeneralPartsListingXlsx('report.general.parts.listing.xls', 'product.product')
