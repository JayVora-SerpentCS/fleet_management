# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import base64
from odoo import models


class FleetHistoryWorkOrder(models.AbstractModel):
    _name = 'report.fleet_operations.fleet.history.work.order.xls'
    _inherit = 'report.report_xlsx.abstract'

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

    def get_identification(self, vehicles_id):
        ident = ""
        if vehicles_id:
            if vehicles_id.name:
                ident += vehicles_id.name or ''
            if vehicles_id.f_brand_id:
                ident += ' ' + vehicles_id.f_brand_id.name or ''
            if vehicles_id.model_id:
                ident += ' ' + vehicles_id.model_id.name or ''
        return ident

    def get_wo_status(self, status):

        wo_status = ""

        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        else:
            wo_status = "New"
        return wo_status

    def generate_xlsx_report(self, workbook, data, workorder):
        worksheet = workbook.add_worksheet('fleet_history_work_order')
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 35)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 10)
#        result = self.get_heading()

        size = workbook.add_format({'bold': True,
                                    'font_name': 'Arial',
                                    'font_size': '12',
                                    'underline': True})
        tit = workbook.add_format({'border': 2,
                                   'font_name': 'Arial',
                                   'font_size': '12'})
        tot = workbook.add_format({'border': 2,
                                   'bold': True,
                                   'font_name': 'Arial',
                                   'font_size': '10'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
#        worksheet.merge_range('C2:D2', 'Merged Cells', merge_format)

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
        worksheet.write(row, 1, 'Work Order', tit)
        row = 2
        for order in workorder:
            row += 3
            worksheet.write(row, 6, 'Work Order No :', tot)
            worksheet.write(row, 7, order.name or '', border)
            row += 1
            worksheet.write(row, 6, 'Actual Date Issued :', tot)
            worksheet.write(row, 7, order.date or '', border)
            row += 1
            worksheet.write(row, 6, 'Status :', tot)
            worksheet.write(row, 7, self.get_wo_status(order.state), border)
            row += 1
            worksheet.write(row, 1, order.team_id and
                            order.team_id.name or '', border)
            worksheet.write(row, 6, 'WO Date Closed', tot)
            worksheet.write(row, 7, order.date_close or '', border)
            row += 3
            worksheet.write(row, 0, 'VEHICLE INFORMATION', size)
            worksheet.write(row, 6, 'ASSIGNMENT', size)
            row += 2
            worksheet.write(row, 0, 'Identification :', tot)
            worksheet.write(row, 1, self.get_identification(order.vehicle_id),
                            border)
            worksheet.write(row, 6, 'Driver Name :', tot)
            worksheet.write(row, 7, order.vehicle_id and
                            order.vehicle_id.driver_id and
                            order.vehicle_id.driver_id.name or '', border)

            row += 1
            worksheet.write(row, 0, 'Vehicle ID :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.name or '', border)
            worksheet.write(row, 2, 'Kilometer :', tot)
            worksheet.write(row, 3, order.odometer or '', border)
            worksheet.write(row, 6, 'Driver Contact No :', tot)
            worksheet.write(row, 7, order.vehicle_id and
                            order.vehicle_id.driver_contact_no or '', border)
            row += 1
            worksheet.write(row, 0, 'VIN No :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.vin_sn or '', border)
            worksheet.write(row, 2, 'Engine No :', tot)
            worksheet.write(row, 3, order.vehicle_id and
                            order.vehicle_id.engine_no or '', border)
            worksheet.write(row, 6, 'Registration State :', tot)
            worksheet.write(row, 7, order.vechical_location_id and
                            order.vechical_location_id.name or '', border)
            row += 1
            worksheet.write(row, 0, 'Vehicle Type :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.vechical_type_id and
                            order.vehicle_id.vechical_type_id.name or '',
                            border)
            worksheet.write(row, 2, 'Plate No :', tot)
            worksheet.write(row, 3, order.vehicle_id and
                            order.vehicle_id.license_plate or '', border)
            row += 1
            worksheet.write(row, 0, 'Vehicle Color :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.vehical_color_id and
                            order.vehicle_id.vehical_color_id.name or '',
                            border)
            row += 3
            worksheet.write(row, 0, 'REPAIRS PERFORMED', size)
            row += 2
            worksheet.write(row, 0, 'No', tot)
            worksheet.write(row, 1, 'Repair Type', tot)
            worksheet.write(row, 2, 'Date', tot)
            worksheet.write(row, 3, 'Category', tot)
            worksheet.write(row, 4, 'Complete', tot)
            line_row = row + 1
            line_col = 0
            counter = 1
            for repair_line in order.repair_line_ids:
                if repair_line.complete is True:
                    worksheet.write(line_row, line_col, counter, border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.repair_type_id and
                                    repair_line.repair_type_id.name or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.target_date, border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.categ_id and
                                    repair_line.categ_id.name or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col, 'True', border)
                    line_row += 1
                    line_col = 0
                if repair_line.complete is False:
                    worksheet.write(line_row, line_col, counter, border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.repair_type_id and
                                    repair_line.repair_type_id.name or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.target_date, border)
                    line_col += 1
                    worksheet.write(row, 2, repair_line.categ_id and
                                    repair_line.categ_id.name or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col, 'False', border)
                    line_row += 1
                    line_col = 0
        row = line_row + 1
        worksheet.write(row, 0, '**************************')
        worksheet.write(row, 1, '****************************************')
        worksheet.write(row, 2, '**************************')
        worksheet.write(row, 3, '**************************')
        worksheet.write(row, 4, '**************************')
        worksheet.write(row, 5, '**************************')
        worksheet.write(row, 6, '**************************')
        worksheet.write(row, 7, '**************************')
        row += 1
        worksheet.write(row, 0, '**************************')
        worksheet.write(row, 1, '****************************************')
        worksheet.write(row, 2, '**************************')
        worksheet.write(row, 3, '**************************')
        worksheet.write(row, 4, '**************************')
        worksheet.write(row, 5, '**************************')
        worksheet.write(row, 6, '**************************')
        worksheet.write(row, 7, '**************************')
