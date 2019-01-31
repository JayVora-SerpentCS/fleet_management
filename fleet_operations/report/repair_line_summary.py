# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo.osv import osv

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class RepairLineSmry(ReportXlsx):

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
    grand_total_repair_line = 0

    def get_repair_line_detail(self, date_range):
        work_order_obj = self.env['fleet.vehicle.log.services']
        start = datetime.strptime(date_range.get('date_from'), '%Y-%m-%d')
        end = datetime.strptime(date_range.get('date_to'), '%Y-%m-%d')
        work_order_ids = \
            work_order_obj.search([('date', '>=', start.date()),
                                   ('date', '<=', end.date()),
                                   ('state', '=', 'done')])
        repair_line_data = []
        repair_l_dic = {}
        if not work_order_ids:
            raise osv.except_osv(('Warning!'),
                                 ("No Work order found in selected date"))
        if work_order_ids:
            for work_rec in work_order_ids:
                for repaire_l in work_rec.repair_line_ids:
                    if repaire_l.complete is True:
                        rep_type = repaire_l.repair_type_id
                        if rep_type and rep_type.name:
                            if repair_l_dic.get(rep_type.id, False):
                                repair_l_dic[rep_type.id]['count'] += 1
                            else:
                                repair_l_dic[rep_type.id] = \
                                    {
                                        'repair_type':
                                        repaire_l.repair_type_id.name or '',
                                        'count': 1}
                            self.grand_total_repair_line += 1
        for repair_data in repair_l_dic.itervalues():
            repair_line_data.append(repair_data)
        if repair_line_data:
            repair_line_data = \
                sorted(repair_line_data, key=lambda k: k['repair_type'])
        else:
            raise osv.except_osv(('Warning!'),
                                 ("No repair type completed in selected \
                                     work order"))
        return repair_line_data

    def get_grand_total_repair_line(self):
        return self.grand_total_repair_line

    def generate_xlsx_report(self, workbook, data, repair):

        worksheet = workbook.add_worksheet('repair_line')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 15)
        bold = workbook.add_format({'bold': True,
                                    'font_name': 'Arial',
                                    'font_size': '10'})
        tot = workbook.add_format({'border': 2,
                                   'bold': True,
                                   'font_name': 'Arial',
                                   'font_size': '10'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        merge_format = workbook.add_format({'border': 2, 'align': 'center'})
#        worksheet.merge_range('C2:E2', 'Merged Cells', merge_format)
        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)
#        result = self.get_heading()
        res = self.get_grand_total_repair_line()

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
        worksheet.write(row, 2,
                        'REPAIR SUMMARY BY REPAIR TYPE-COMULATIVE', tot)
        row += 2
        worksheet.write(row, 2, 'Date From:', bold)
        worksheet.write(row, 3, data['form']['date_from'] or '', bold)
        worksheet.write(row, 4, 'TO', bold)
        worksheet.write(row, 5, data['form']['date_to'], bold)
        row += 2
        worksheet.write(row, 0, 'No.', format1)
        worksheet.write(row, 1, 'REPAIR TYPE:', format1)
        worksheet.write(row, 2, 'COUNT', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for repair_line in self.get_repair_line_detail(data['form']):
            worksheet.write(line_row, line_col, counter, border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            repair_line.get('repair_type'), border)
            res += 1
            line_col += 1
            worksheet.write(line_row, line_col,
                            repair_line.get('count'), border)
            line_row += 1
            line_col = 0
            counter += 1
        row = line_row + 1
        worksheet.write(row, 1, 'Grand Total', border)
        worksheet.write(row, 2, res, border)


RepairLineSmry('report.repair.line.summary.xls', 'repair.line.summary')
