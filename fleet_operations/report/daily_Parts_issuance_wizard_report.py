# See LICENSE file for full copyright and licensing details.
"""Daily Parts issuance Wizard Report."""

from datetime import datetime, timedelta

from odoo import models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class DailyPartWizard(models.AbstractModel):
    """Daily Part Wizard."""

    _name = 'report.fleet_operations.daily.parts.issuance.wizard.xls'
    _description = 'Daily Parts Insurance'

    def get_heading(self):
        """Report Method."""
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

    def get_work_order_detail(self, date_range):
        """Report Method to Get Work Order Details."""
        work_order_obj = self.env['task.line']
        start = datetime.strptime(date_range.get('date_from'), '%Y-%m-%d')
        end = datetime.strptime(date_range.get('date_to'), '%Y-%m-%d')
        step = timedelta(days=1)
        workorder_detail = []
        while start <= end:
            sdate = str(datetime.strptime(str(start.date()) + ' 00:00:00',
                                          DEFAULT_SERVER_DATETIME_FORMAT))
            edate = str(datetime.strptime(str(start.date()) + ' 23:59:59',
                                          DEFAULT_SERVER_DATETIME_FORMAT))
            work_order_ids = work_order_obj.search([('date_issued', '>=',
                                                     sdate), ('date_issued',
                                                              '<=', edate)])
            if work_order_ids:
                parts_data = {}
                parts_value = []
                for parts_line in work_order_ids:
                    if parts_line.fleet_service_id and \
                            parts_line.fleet_service_id.state == 'done':
                        parts_dict = {
                            'wo_name': parts_line.fleet_service_id and
                            parts_line.fleet_service_id.name or '',
                            'vehicle_id': parts_line.fleet_service_id and
                            parts_line.fleet_service_id.vehicle_id and
                            parts_line.fleet_service_id.vehicle_id.name or '',
                            'part_no': parts_line.product_id and
                            parts_line.product_id.default_code or '',
                            'part_name': parts_line.product_id and
                            parts_line.product_id.name or '',
                            'vehicle_make': parts_line.vehicle_make_id and
                            parts_line.vehicle_make_id.name or '',
                            'qty': parts_line.qty or 0.0,
                            'uom': parts_line.product_uom and
                            parts_line.product_uom.name or '',
                            'old_part_return': parts_line.old_part_return and
                            'Yes' or 'No',
                            'issued_by': parts_line.issued_by and
                            parts_line.issued_by.name or '',
                            'remarks': parts_line.fleet_service_id and
                            parts_line.fleet_service_id.note or ''
                        }
                        parts_value.append(parts_dict)
                if parts_value:
                    parts_value = sorted(parts_value,
                                         key=lambda k: k['wo_name'])
                    parts_data = {
                        'date': start.date(),
                        'value': parts_value
                    }
                    workorder_detail.append(parts_data)
            start += step
        return workorder_detail

    def generate_xlsx_report(self, workbook, data, parts_data):
        """Generate xlsx format print report."""
        worksheet = workbook.add_worksheet('daily_parts_issuance_wizard')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(10, 10, 15)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 20)
        worksheet.set_column(13, 13, 5)
        worksheet.set_column(14, 14, 5)
        worksheet.set_column(15, 15, 5)

        bold = workbook.add_format({'bold': True,
                                    'font_name': 'Arial',
                                    'font_size': '10'})
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
        date = workbook.add_format({'num_format': 'dd/mm/yy'})

        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'DAILY PARTS ISSUANCE', tot)
        row += 1
        worksheet.write(row, 2, 'Date From:', tot)
        worksheet.write(row, 3, data['form']['date_from'] or '', border)
        worksheet.write(row, 4, 'To:', tot)
        worksheet.write(row, 5, data['form']['date_to'] or '', border)
        row += 2
        worksheet.write(row, 0, 'CMF', bold)
        row = 3

        for objec in self.get_work_order_detail(data['form']):
            row += 3
            worksheet.write(row, 0, 'DATE ISSUED :', bold)
            worksheet.write(row, 1, objec.get('date') or '', date)
            row += 2
            worksheet.write(row, 0, 'NO.', format1)
            worksheet.write(row, 1, 'WO NO.', format1)
            worksheet.write(row, 2, 'VEHICLE ID', format1)
            worksheet.write(row, 3, 'PART NO.', format1)
            worksheet.write(row, 4, 'PART NAME', format1)
            worksheet.write(row, 5, 'VEHICLE MAKE', format1)
            worksheet.write(row, 6, 'USED', format1)
            worksheet.write(row, 7, 'UNIT TYPE', format1)
            worksheet.write(row, 8, 'OLD PART RETURND', format1)
            worksheet.write(row, 9, 'ISSUED BY', format1)
            worksheet.write(row, 10, 'REMARKS', format1)
            line_row = row + 1
            line_col = 0
            counter = 1
            for obj in objec.get('value'):
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('wo_name') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('vehicle_id') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('part_no') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('part_name') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('vehicle_make') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('qty') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('uom') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('old_part_return') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('issued_by') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('remarks') or '', border)
                line_col = 0
                line_row += 1
                counter += 1
                worksheet.write(line_row, line_col, '********', border)
