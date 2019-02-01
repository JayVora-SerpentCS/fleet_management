# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class OldPartReturn(ReportXlsx):

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

    def get_old_part_detail(self, date_range):
        work_order_obj = self.env['fleet.vehicle.log.services']
        start = datetime.strptime(date_range.get('date_from'), '%Y-%m-%d')
        end = datetime.strptime(date_range.get('date_to'), '%Y-%m-%d')
        step = timedelta(days=1)
        workorder_detail = []
        while start <= end:
            work_order_ids = \
                work_order_obj.search([('date_close', '=', start.date()),
                                       ('state', '=', 'done')])
            if work_order_ids:
                parts_data = {}
                parts_value = []
                for work_order in work_order_ids:
                    for inc_shiping in work_order.old_parts_incoming_ship_ids:
                        if inc_shiping.state == 'done':
                            for parts_line in inc_shiping.move_lines:
                                parts_dict = {
                                    'part_no': parts_line.product_id and
                                    parts_line.product_id.default_code or '',
                                    'part_name': parts_line.product_id and
                                    parts_line.product_id.name or '',
                                    'qty': parts_line.product_qty or 0.0,
                                    'uom': parts_line.product_uom and
                                    parts_line.product_uom.name or '',
                                }
                                parts_value.append(parts_dict)
                if parts_value:
                    parts_data = {
                        'date': start.date(),
                        'value': parts_value
                    }
                    workorder_detail.append(parts_data)
            start += step
        return workorder_detail

    def generate_xlsx_report(self, workbook, data, part):
        worksheet = workbook.add_worksheet('old_part_return_wizard')
        worksheet.set_column(0, 0, 13)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 10)
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
                                       'font_size': '10',
                                       'num_format': 'dd/mm/yy'})
#        worksheet.merge_range('C2:E2', 'Merged Cells', merge_format)
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
#        worksheet.write(row, 5, 'Rev. No. :', tot)
#        worksheet.write(row, 6, result.get('rev_no') or '', border)
#        worksheet.write(row, 7, 'Document No. :', tot)
#        worksheet.write(row, 8, result.get('doc_no') or '', border)
        row += 1
        worksheet.write(row, 2, 'Old Part Return', tot)
        row += 1
        worksheet.write(row, 2, 'Range From:', tot)
        worksheet.write(row, 3, data['form']['date_from'] or '', border)
        worksheet.write(row, 4, 'To', tot)
        worksheet.write(row, 5, data['form']['date_to'] or '', border)
        for obj in self.get_old_part_detail(data['form']):
            row += 3
            worksheet.write(row, 0, 'DATE RECIEVED :', tot)
            worksheet.write(row, 1, obj['date'], format1)
            row += 2
            worksheet.write(row, 0, 'No.', format1)
            worksheet.write(row, 1, 'Part Number', format1)
            worksheet.write(row, 2, 'Name and Discription', format1)
            worksheet.write(row, 3, 'QTY', format1)
            worksheet.write(row, 4, 'UOM', format1)
            line_row = row + 1
            line_col = 0
            counter = 1
            for line in self.get_old_part_detail(data['form']):
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col, line['value']
                                [0].get('part_no') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, line['value']
                                [0].get('part_name') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, line['value']
                                [0].get('qty') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col, line['value']
                                [0].get('uom') or '', border)
                line_col = 0
                line_row += 1
                counter += 1
                worksheet.write(line_row, line_col, '********', border)


OldPartReturn('report.old.part.return.wizard.xls', 'part.summary')
