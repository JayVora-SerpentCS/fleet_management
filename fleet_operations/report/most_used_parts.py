# See LICENSE file for full copyright and licensing details.
"""Most Used Parts Report."""


from odoo import models
from odoo.exceptions import UserError


class MostUsedPartsXlsx(models.AbstractModel):
    """Most used parts xlsx."""

    _name = 'report.fleet_operations.most.used.parts.xls'
    _description = 'Most Used Parts Report'

    most_part_used_garnd_total = 0.0

    def get_grand_total(self):
        """Method to get grand total."""
        return self.most_part_used_garnd_total

    def get_most_used_parts(self, date_range, top_no):
        """Method to get most used parts."""
        work_order_obj = self.env['task.line']
        part_list_data = []
        used_dict = {}
        work_order_ids = \
            work_order_obj.search(
                [('date_issued', '>=', date_range.get('date_from')),
                 ('date_issued', '<=', date_range.get('date_to'))])
        if work_order_ids:
            for p_line in work_order_ids:
                if p_line.fleet_service_id and \
                        p_line.fleet_service_id.state == 'done':
                    if used_dict.get(p_line.product_id.id, False):
                        used_dict[p_line.product_id.id]['qty'] += \
                            p_line.qty or 0.0
                        used_dict[p_line.product_id.id]['total_cost'] = \
                            used_dict[p_line.product_id.id]['qty'] * \
                            p_line.product_id.standard_price
                    else:
                        used_dict[p_line.product_id.id] = \
                            {
                                'part_no': p_line.product_id and
                                p_line.product_id.default_code or '',
                                'part_name': p_line.product_id and
                                p_line.product_id.name or '',
                                'vehicle_make': p_line.product_id and
                                p_line.product_id.vehicle_make_id and
                                p_line.product_id.vehicle_make_id.name or '',
                                'qty': p_line.qty or 0.0,
                                'qty_available': p_line.product_id and
                                p_line.product_id.qty_available,
                                'uom': p_line.product_id and
                                p_line.product_id.uom_id and
                                p_line.product_id.uom_id.name or '',
                                'unit_cost': p_line.product_id and
                                p_line.product_id.standard_price or 0.0,
                                'total_cost':
                                p_line.qty * p_line.product_id.standard_price}

        for part_data in used_dict.itervalues():
            part_list_data.append(part_data)
        if part_list_data:
            part_list_data = sorted(part_list_data,
                                    key=lambda k: k['qty'], reverse=True)
        else:
            raise UserError("Warning! \n\
                    No parts were used in selected date.")

        flag = 1
        final_data = []
        for data in part_list_data:
            if flag <= top_no:
                self.most_part_used_garnd_total += data.get('total_cost')
                final_data.append(data)
            else:
                break
            flag += 1
        return final_data

    def generate_xlsx_report(self, workbook, data, parts):
        """Method to generate xlsx report."""
        worksheet = workbook.add_worksheet('product')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
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
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        merge_format = workbook.add_format({'border': 2, 'align': 'center'})
        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)
        res = self.get_grand_total()
        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'MOST USED PARTS', tot)
        row += 2
        worksheet.write(row, 2, 'Date From:', bold)
        worksheet.write(row, 3, data['form']['date_from'] or '')
        worksheet.write(row, 4, 'TO', bold)
        worksheet.write(row, 5, data['form']['date_to'] or '')
        row += 2
        worksheet.write(row, 0, 'No.', format1)
        worksheet.write(row, 1, 'Part No:', format1)
        worksheet.write(row, 2, 'Part Name', format1)
        worksheet.write(row, 3, 'Vehicle Make', format1)
        worksheet.write(row, 4, 'Qty on hand ', format1)
        worksheet.write(row, 5, 'Used', format1)
        worksheet.write(row, 6, 'Unit Type ', format1)
        worksheet.write(row, 7, 'Unit Cost ', format1)
        worksheet.write(row, 8, 'Total Cost', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for parts_value in self.get_most_used_parts(data['form'],
                                                    data['form']['top_no']):
            worksheet.write(line_row, line_col, counter, border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('part_no'), border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('part_name'), border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('vehicle_make'), border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('qty_available'), border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('qty'), border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('uom'), border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('unit_cost'), border)
            line_col += 1
            worksheet.write(line_row, line_col,
                            parts_value.get('total_cost'), border)
            line_row += 1
            line_col = 0
            counter += 1
        row = line_row + 1
        row += 3
        worksheet.write(row, 7, 'Grand Total Cost', border)
        worksheet.write(row, 8, res, border)
