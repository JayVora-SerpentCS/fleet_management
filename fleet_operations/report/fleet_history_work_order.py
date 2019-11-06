# See LICENSE file for full copyright and licensing details.
"""Fleet History Work Order Report."""


import base64
import io

from odoo import models

import xlwt


class FleetHistoryWorkOrder(models.AbstractModel):
    """Fleet History Work Order."""

    _name = 'report.fleet_operations.fleet.history.work.order.xls'
    _description = 'Fleet History Work Order'

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

    def get_identification(self, vehicles_id):
        """Method get identification."""
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
        """Method get wo status."""
        wo_status = ""

        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        else:
            wo_status = "New"
        return wo_status

    def generate_xlsx_report(self, workorder):
        """Generate report xlsx."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('fleet_history_work_order')
        worksheet.col(0).width = 7500
        worksheet.col(1).width = 17000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 7500
        worksheet.col(5).width = 7500
        worksheet.col(6).width = 10000
        worksheet.col(7).width = 5000

        font = xlwt.Font()
        # borders = xlwt.Borders()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        size = xlwt.easyxf('font: bold 1; font: name 1; font: height 220')
        # tit = xlwt.easyxf('font: name 1; font: height 220')
        tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        # format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
        #     pattern: pattern solid')
        row = 0
        row += 1
        row += 1
        worksheet.write(row, 1, 'Work Order', border)
        row = 2
        for order in workorder:
            row += 3
            worksheet.write(row, 6, 'Service Order :', tot)
            worksheet.write(row, 7, order.name or '')
            row += 1
            worksheet.write(row, 6, 'Actual Date Issued :', tot)
            worksheet.write(row, 7, order.date or '')
            row += 1
            worksheet.write(row, 6, 'Status :', tot)
            worksheet.write(row, 7, self.get_wo_status(order.state))
            row += 1
            worksheet.write(row, 1, order.team_id and
                            order.team_id.name or '')
            worksheet.write(row, 6, 'WO Date Closed', tot)
            worksheet.write(row, 7, order.date_close or '')
            row += 3
            worksheet.write(row, 0, 'VEHICLE INFORMATION', size)
            worksheet.write(row, 6, 'ASSIGNMENT', size)
            row += 2
            worksheet.write(row, 0, 'Identification :', tot)
            worksheet.write(row, 1, self.get_identification(order.vehicle_id))
            worksheet.write(row, 6, 'Driver Name :', tot)
            worksheet.write(row, 7, order.vehicle_id and
                            order.vehicle_id.driver_id and
                            order.vehicle_id.driver_id.name or '')

            row += 1
            worksheet.write(row, 0, 'Vehicle ID :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.name or '')
            worksheet.write(row, 2, 'Kilometer :', tot)
            worksheet.write(row, 3, order.odometer or '')
            worksheet.write(row, 6, 'Driver Contact No :', tot)
            worksheet.write(row, 7, order.vehicle_id and
                            order.vehicle_id.driver_contact_no or '')
            row += 1
            worksheet.write(row, 0, 'VIN No :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.vin_sn or '')
            worksheet.write(row, 2, 'Engine No :', tot)
            worksheet.write(row, 3, order.vehicle_id and
                            order.vehicle_id.engine_no or '')
            worksheet.write(row, 6, 'Registration State :', tot)
            worksheet.write(row, 7, order.vechical_location_id and
                            order.vechical_location_id.name or '')
            row += 1
            worksheet.write(row, 0, 'Vehicle Type :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.vechical_type_id and
                            order.vehicle_id.vechical_type_id.name or '')
            worksheet.write(row, 2, 'Plate No :', tot)
            worksheet.write(row, 3, order.vehicle_id and
                            order.vehicle_id.license_plate or '')
            row += 1
            worksheet.write(row, 0, 'Vehicle Color :', tot)
            worksheet.write(row, 1, order.vehicle_id and
                            order.vehicle_id.vehical_color_id and
                            order.vehicle_id.vehical_color_id.name or '')
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
                    worksheet.write(line_row, line_col, counter)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.repair_type_id and
                                    repair_line.repair_type_id.name or '')
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.target_date)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.categ_id and
                                    repair_line.categ_id.name or '')
                    line_col += 1
                    worksheet.write(line_row, line_col, 'True')
                    line_row += 1
                    line_col = 0
                if repair_line.complete is False:
                    worksheet.write(line_row, line_col, counter)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.repair_type_id and
                                    repair_line.repair_type_id.name or '')
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    repair_line.target_date)
                    line_col += 1
                    worksheet.write(row, 2, repair_line.categ_id and
                                    repair_line.categ_id.name or '')
                    line_col += 1
                    worksheet.write(line_row, line_col, 'False')
                    line_row += 1
                    line_col = 0
        line_row = row + 1
        worksheet.write(row, 0, '**************************')
        worksheet.write(row, 1, '**************************')
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
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
