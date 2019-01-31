# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):

        def __init__(self, *args, **kwargs):
            pass


class VehicleChangeHistory(ReportXlsx):

    def get_vehicle_history(self, date_range):
        engine_obj = self.env['engine.history']
        color_obj = self.env['color.history']
        vin_obj = self.env['vin.history']
        domain = []
        if date_range.get('date_from'):
            domain += [('changed_date', '>=', date_range.get('date_from'))]
        if date_range.get('date_to'):
            domain += [('changed_date', '<=', date_range.get('date_to'))]
        if date_range.get('fleet_id'):
            domain += [('vehicle_id', '=', date_range.get('fleet_id'))]

        engine_ids = engine_obj.search(domain)
        color_ids = color_obj.search(domain)
        vin_ids = vin_obj.search(domain)
        vehicle_change_history = []
        if engine_ids:
            for engine_rec in engine_ids:
                seq = engine_rec.vehicle_id and \
                    engine_rec.vehicle_id.name or ''
                values = {}
                values = {
                    'description': seq,
                    'vehicle_type': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vechical_type_id and
                    engine_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vehical_color_id and
                    engine_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': engine_rec.previous_engine_no or '',
                    'new_engine': engine_rec.new_engine_no or '',
                    'old_color': '',
                    'new_color': '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date': engine_rec.changed_date or False,
                    'work_order': engine_rec.workorder_id and
                    engine_rec.workorder_id.name or '',
                    'wo_close_date': engine_rec.workorder_id and
                    engine_rec.workorder_id.date_close or False,
                    'remarks': engine_rec.note or '',
                    'seq': seq + 'a'
                }
                vehicle_change_history.append(values)
        if color_ids:
            for color_rec in color_ids:
                seq = color_rec.vehicle_id and color_rec.vehicle_id.name or ''
                cvalues = {}
                cvalues = {
                    'description': seq,
                    'vehicle_type': color_rec.vehicle_id and
                    color_rec.vehicle_id.vechical_type_id and
                    color_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': color_rec.vehicle_id and
                    color_rec.vehicle_id.vehical_color_id and
                    color_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': color_rec.vehicle_id and
                    color_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': '',
                    'new_engine': '',
                    'old_color': color_rec.previous_color_id and
                    color_rec.previous_color_id.name or '',
                    'new_color': color_rec.current_color_id and
                    color_rec.current_color_id.name or '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date': color_rec.changed_date or False,
                    'work_order': color_rec.workorder_id and
                    color_rec.workorder_id.name or '',
                    'wo_close_date': color_rec.workorder_id and
                    color_rec.workorder_id.date_close or False,
                    'remarks': color_rec.note or '',
                    'seq': seq + 'b'
                }
                vehicle_change_history.append(cvalues)
        if vin_ids:
            for vin_rec in vin_ids:
                seq = vin_rec.vehicle_id and vin_rec.vehicle_id.name or ''
                vvalues = {}
                vvalues = {
                    'description': seq,
                    'vehicle_type': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vechical_type_id and
                    vin_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vehical_color_id and
                    vin_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': '',
                    'new_engine': '',
                    'old_color': '',
                    'new_color': '',
                    'old_vin': vin_rec.previous_vin_no or '',
                    'new_vin': vin_rec.new_vin_no or '',
                    'change_date': vin_rec.changed_date or False,
                    'work_order': vin_rec.workorder_id and
                    vin_rec.workorder_id.name or '',
                    'wo_close_date': vin_rec.workorder_id and
                    vin_rec.workorder_id.date_close or False,
                    'remarks': vin_rec.note or '',
                    'seq': seq + 'c'
                }
                vehicle_change_history.append(vvalues)
        if vehicle_change_history:
            vehicle_change_history = sorted(vehicle_change_history,
                                            key=lambda k: k['seq'])
        return vehicle_change_history

    def generate_xlsx_report(self, workbook, data, vehicle):
        worksheet = workbook.add_worksheet('vehicle_change_histoty')
        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(10, 10, 10)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 20)
        worksheet.set_column(13, 13, 10)
        tot = workbook.add_format({'border': 2,
                                   'bold': True,
                                   'font_name': 'Arial',
                                   'font_size': '10'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        merge_format = workbook.add_format({'align': 'center'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        worksheet.merge_range('A2:N2', 'Merged Cells', merge_format)
        worksheet.merge_range('G4:H4', 'Merged Cells', merge_format)
        worksheet.merge_range('I4:J4', 'Merged Cells', merge_format)
        row = 1
        worksheet.write(row, 0, 'List of the Vehicle Which Engine and color \
                                    has changed in CMF workshop', tot)
        row += 2
        worksheet.write(row, 6, 'Engine History', format1)
        worksheet.write(row, 8, 'Color History', format1)
        row += 1
        worksheet.write(row, 0, 'No.', format1)
        worksheet.write(row, 1, 'Description', format1)
        worksheet.write(row, 2, 'Type of Vehicle', format1)
        worksheet.write(row, 3, 'Vehicle Color ', format1)
        worksheet.write(row, 4, 'Vehicle VIN # ', format1)
        worksheet.write(row, 5, 'Plate #', format1)
        worksheet.write(row, 6, 'Old Engine # ', format1)
        worksheet.write(row, 7, 'New Engine # ', format1)
        worksheet.write(row, 8, 'Old Color ', format1)
        worksheet.write(row, 9, 'New color ', format1)
        worksheet.write(row, 10, 'Old Vin ', format1)
        worksheet.write(row, 11, 'New Vin ', format1)
        worksheet.write(row, 10, 'Change Date', format1)
        worksheet.write(row, 11, 'Work Order No', format1)
        worksheet.write(row, 12, 'Work Order Closed Date', format1)
        worksheet.write(row, 13, 'Remarks ', format1)
        result = self.get_vehicle_history(data['form'])
        line_row = row + 1
        line_col = 0
        counter = 1
        row += 1
        for obj in result:
            worksheet.write(line_row, line_col, counter, border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['description'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['vehicle_type'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['color_id'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['vin'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['plate'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['old_engine'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['new_engine'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['old_color'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['new_color'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['change_date'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['work_order'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['wo_close_date'] or '',
                            border)
            line_col += 1
            worksheet.write(line_row, line_col, obj['remarks'] or '',
                            border)
            line_col = 0
            line_row += 1
            counter += 1
            worksheet.write(line_row, line_col, '********', border)


VehicleChangeHistory('report.vehicle.change.history.xls',
                     'vehicle.change.history')
